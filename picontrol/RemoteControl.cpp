#include <iostream>
#include <cstring>
#include <mosquitto.h>

#include <gpiod.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>

#include "json.hpp"
using json = nlohmann::json;
json json_data;

json pgm_dispatch = json::parse(R"(
{
	"CartControl" : "CartControlPiMod2.elf",
	"CartIdent" : "CartIdentPiMod2.elf",
	"CraneIdent" : "CraneIdentPiMod2.elf",
	"CraneStab" : "CraneStabPiMod2.elf",
	"InvPendIdent" : "InvPendIdentPiMod2.elf",
	"PendStabPD" : "PendStabPDPiMod2.elf",
	"PendSwingUp" : "PendSwingUpPiMod2.elf",
	"PendulumFriction" : "PendulumFrictionPiMod2.elf",
	"PendulumTest" : "PendulumTestPiMod2.elf",
	"SwingHoldPendulum" : "SwingHoldPendulumPiMod2.elf",
	"SwingHoldPendulumExtra" : "SwingHoldPendulumExtraPiMod2.elf",
	"UpDownPendulum" : "UpDownPendulumPiMod2.elf"
}
)");
	
std::string expState = "initialized";
std::string sim_pgm = "";

const char *chipname = "gpiochip0";
const char *linenameStart = "GPIO23";
const char *linenameStop = "GPIO24";
const char *linenameRecenter = "GPIO25";
const char *linenameReset = "GPIO6";
struct gpiod_chip *chip;
struct gpiod_line *lineStart;
struct gpiod_line *lineStop;
struct gpiod_line *lineRecenter;
struct gpiod_line *lineReset;
//######################################################################################################################################################################################
// Dispatch to simulink program
//######################################################################################################################################################################################

static void dispatch_to_simulink(std::string exp, json parameters) {
	const std::string library = "/home/owlsley/MATLAB_ws/R2025b";
	sim_pgm = pgm_dispatch[exp];
	
	std::cout << "Dispatching to program " << sim_pgm << " with parameters: " << parameters.dump() << std::endl;
	// Here you would add the actual code to send the command and parameters to the Simulink program, e.g., via a socket or shared memory.
		
	std::cout << "Started Simulink program " << sim_pgm << std::endl;
	int retval = system(("sudo "+library + "/" + sim_pgm + " &").c_str());
	if (retval == -1) {
		std::cerr << "Failed to execute Simulink program." << std::endl;
	}
}


static void kill_simulink() {
	std::cout << "Killing Simulink program " << sim_pgm << std::endl;
	int retval = system(("ps -ef | grep "+sim_pgm + " | awk '{print $2}' | xargs kill &").c_str());
	if (retval == -1) {
		std::cerr << "Failed to kill Simulink program." << std::endl;
	}
}
//######################################################################################################################################################################################
// Setup parameter file
//######################################################################################################################################################################################

//######################################################################################################################################################################################
// Message actions
//######################################################################################################################################################################################

static void push_start_button() {

};


static void push_stop_button() {
	
}

static void push_recenter_button() {

}
//########################################################################################################################################################################################
// Status Light actions
//########################################################################################################################################################################################


void status_light(std::string cmd)
{
	
	chip = gpiod_chip_open_by_name(chipname);
	if (!chip) {
		perror("Open chip failed\n");
		return;
	}
	
	lineStart = gpiod_chip_find_line(chip, linenameStart);
	if (!lineStart) {
		perror("Find lineStart failed\n");
		gpiod_chip_close(chip);
		return;
	}
	lineStop = gpiod_chip_find_line(chip, linenameStop);
	if(!lineStop) {
		perror("Find lineStop failed\n");
		gpiod_chip_close(chip);
		return;
	}
	lineRecenter = gpiod_chip_find_line(chip, linenameRecenter);
	if (!lineRecenter) {
		perror("Find lineRecenter failed\n");
		gpiod_chip_close(chip);
		return;
	}
	
	if (gpiod_line_request_output(lineStart, "gpio_test", 0) < 0) {
		perror("Request lineStart as output failed\n");
		gpiod_chip_close(chip);
		return;
	}
	if (gpiod_line_request_output(lineStop, "gpio_test", 0) < 0) {
		perror("Request lineStop as output failed\n");
		gpiod_chip_close(chip);
		return;
	}
	if (gpiod_line_request_output(lineRecenter, "gpio_test", 0) < 0) {
		perror("Request lineRecenter as output failed\n");
		gpiod_chip_close(chip);
		return;	
	}
	
	if (cmd == "sta") {
		expState = "running";
		gpiod_line_set_value(lineStart, 1);		// On
		gpiod_line_set_value(lineStop, 0);		// Off
		gpiod_line_set_value(lineRecenter, 0);	// Off
	} else if (cmd == "sto") {
		expState = "stopped";
		gpiod_line_set_value(lineStart, 0);		// Off
		gpiod_line_set_value(lineStop, 1);		// On
		gpiod_line_set_value(lineRecenter, 0);	// Off
	} else if (cmd == "rec") {
		expState = "recentered";
		gpiod_line_set_value(lineStart, 0);		// Off
		gpiod_line_set_value(lineStop, 0);		// Off
		gpiod_line_set_value(lineRecenter, 1);	// On
	} else {
			printf("Unknown lights command: %s\n", cmd);
	}
	
	gpiod_line_release(lineStart);
	gpiod_chip_close(chip);
}
//########################################################################################################################################################################################
// MQTT message processing
//########################################################################################################################################################################################
void process_message(std::string payload) {

	json_data = json::parse(payload);
	
	auto command = json_data.find("command");
	std::cout << "Received command: " << *command << std::endl;
	
	auto experiment = json_data.find("experiment");
	std::cout << "Experiment: " << *experiment << std::endl;	
	

	
	if (*command == "sta") {
		auto parameters = json_data.find("parameters");
		std::cout << "Parameters: " << *parameters << std::endl;
		
		status_light(*command);
		dispatch_to_simulink(*experiment, *parameters);
		push_start_button();
	}
	else if (*command == "sto") {
		status_light(*command);
		kill_simulink();
		push_stop_button();
	}
	else if (*command == "rec") {
		status_light(*command);
		push_recenter_button();
	}
	else {
		printf("Unknown command: %s\n", payload);
	}
}

//##################
// MQTT actions    #
//##################
// Callback when the client connects to the broker
void on_connect(struct mosquitto *mosq, void *userdata, int rc) {
	if (rc == 0) {
		std::cout << "Connected to broker successfully." << std::endl;
		// Subscribe to a topic
		const char* topic = "pendulum/cmd";
		int ret = mosquitto_subscribe(mosq, nullptr, topic, 0);
		if (ret != MOSQ_ERR_SUCCESS) {
			std::cerr << "Failed to subscribe: " << mosquitto_strerror(ret) << std::endl;
		}
		else {
			std::cout << "Subscribed to topic " << topic << std::endl;
		}
	}
	else {
		std::cerr << "Connection failed: " << mosquitto_strerror(rc) << std::endl;
	}
}

// Callback when a message is received
void on_message(struct mosquitto *mosq, void *userdata, const struct mosquitto_message *msg) {
	std::cout << "Message received on topic '" << msg->topic << "': "
	          << (msg->payloadlen ? (char*)msg->payload : "(empty)") << std::endl;
	std::string message;
	message = (char*)msg->payload;	
	process_message(message);
}

// Callback when the client disconnects
void on_disconnect(struct mosquitto *mosq, void *userdata, int rc) {
	std::cout << "Disconnected from broker." << std::endl;
}
//########################################################################################################################################################################################
// ADC actions
//########################################################################################################################################################################################
//########################################################################################################################################################################################
// GPIO actions
//########################################################################################################################################################################################
void setup_gpio() {
	// Here you would add code to initialize the GPIO pins, e.g., using gpiod to set up the lines for the status lights and buttons.
	chip = gpiod_chip_open_by_name(chipname);
	if (!chip) {
		perror("Open chip failed\n");
		return;
	}
	
	lineStart = gpiod_chip_find_line(chip, linenameStart);
	if (!lineStart) {
		perror("Find lineStart failed\n");
		gpiod_chip_close(chip);
		return;
	}
	lineStop = gpiod_chip_find_line(chip, linenameStop);
	if (!lineStop) {
		perror("Find lineStop failed\n");
		gpiod_chip_close(chip);
		return;
	}
	lineRecenter = gpiod_chip_find_line(chip, linenameRecenter);
	if (!lineRecenter) {
		perror("Find lineRecenter failed\n");
		gpiod_chip_close(chip);
		return;
	}
	lineReset = gpiod_chip_find_line(chip, linenameReset);
	if (!lineReset) {
		perror("Find lineReset failed\n");
		gpiod_chip_close(chip);
		return;
	}	
	
	if (gpiod_line_request_output(lineStart, "gpio_test", 0) < 0) {
		perror("Request lineStart as output failed\n");
		gpiod_chip_close(chip);
		return;
	}
	if (gpiod_line_request_output(lineStop, "gpio_test", 0) < 0) {
		perror("Request lineStop as output failed\n");
		gpiod_chip_close(chip);
		return;
	}
	if (gpiod_line_request_output(lineRecenter, "gpio_test", 0) < 0) {
		perror("Request lineRecenter as output failed\n");
		gpiod_chip_close(chip);
		return;	
	}
	if (gpiod_line_request_output(lineReset, "gpio_test", 0) < 0) {
		perror("Request lineReset as output failed\n");
		gpiod_chip_close(chip);
		return;	
	}
	
	gpiod_line_set_value(lineStart, 0);		// Off
	gpiod_line_set_value(lineStop, 0);		// Off
	gpiod_line_set_value(lineRecenter, 0);	// Off
	gpiod_line_set_value(lineReset, 0);		// Off}
}
//########################################################################################################################################################################################
// main function
//########################################################################################################################################################################################
int main() {
	const char *host = "sciencelabtoyou.com"; // Change to your broker address
	int port = 1885;
	const char *client_id = "cpp_subscriber";

	// Initialize the Mosquitto library
	mosquitto_lib_init();

	// Create a new Mosquitto client instance
	struct mosquitto *mosq = mosquitto_new(client_id, true, nullptr);
	if (!mosq) {
		std::cerr << "Failed to create Mosquitto instance." << std::endl;
		mosquitto_lib_cleanup();
		return 1;
	}

	// Set callbacks
	mosquitto_connect_callback_set(mosq, on_connect);
	mosquitto_message_callback_set(mosq, on_message);
	mosquitto_disconnect_callback_set(mosq, on_disconnect);

	// Connect to the broker
	int ret = mosquitto_connect(mosq, host, port, 60);
	if (ret != MOSQ_ERR_SUCCESS) {
		std::cerr << "Unable to connect: " << mosquitto_strerror(ret) << std::endl;
		mosquitto_destroy(mosq);
		mosquitto_lib_cleanup();
		return 1;
	}

	// Start the network loop (blocking)
	mosquitto_loop_forever(mosq, -1, 1);

	// Cleanup
	std::cout << "Clean-up" << std::endl;
	mosquitto_destroy(mosq);
	mosquitto_lib_cleanup();

	return 0;
}
//******************************************************************************************************************************************************************************************/
// Remote control of pendulum experiment via MQTT messages, with status light feedback and Simulink program dispatching */
//******************************************************************************************************************************************************************************************/


//******************************************************************************************************************************************************************************************/
//* Simulink Functions */
//******************************************************************************************************************************************************************************************/
//* Setup Simulink */
void setupSimulink() {
	return;
} 

//******************************************************************************************************************************************************************************************/
//* MQTT Functions */
//******************************************************************************************************************************************************************************************/
//* Setup MQTT */
void setupMQTT() {
	return;
}
//******************************************************************************************************************************************************************************************/
//* ADC Functions */
//******************************************************************************************************************************************************************************************/
//* Setup ADC */
void setupADC() {
	return;
}

//******************************************************************************************************************************************************************************************/
//* I2C Functions */
//******************************************************************************************************************************************************************************************/
//* Setup I2C */
void setupI2C() {
	return;
}

//******************************************************************************************************************************************************************************************/
//* GPIO Functions */
//******************************************************************************************************************************************************************************************/
//* Setup GPIO */
void setupGPIO() {
	return;
}
//******************************************************************************************************************************************************************************************/
//* Main Function */
//******************************************************************************************************************************************************************************************/
int main() {

	setupADC();
	setupI2C();
	setupGPIO();
	setupMQTT();
	setupSimulink();
	
	while (true) {
		// Main loop can be used for other tasks if needed
		sleep(1);
	}
	
	return 0;
}