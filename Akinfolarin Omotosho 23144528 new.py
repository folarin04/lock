import pexpect
import logging

# Set up logging
logging.basicConfig(filename='network_device_config.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
credentials = {
    "ip": '192.168.56.101',
    "username": 'prne',
    "password": 'cisco123!',
    "enable_password": 'class123!'
}

def configure_device(session, protocol): 
    """Configure the device by setting the hostname."""
    try:
        session.sendline('configure terminal')
        session.expect(r'\(config\)#')
        logging.info('Entered configuration mode')
        
        session.sendline('hostname R1')
        session.expect(r'R1\(config\)#')
        logging.info('Hostname set to R1')
        
        session.sendline('exit')
        session.sendline('exit')
        logging.info('Exited configuration mode and closed session')
    except Exception as e:
        logging.error(f"Error during device configuration: {e}")
        
    session.close()
    print_success(protocol)

def print_success(protocol):
    """Print a success message."""
    print('---------------------------------------------')
    print(f'--- Success! {protocol.upper()} connection established to {credentials["ip"]}')
    print(f'    Username: {credentials["username"]}')
    print('---------------------------------------------')
    logging.info(f'Successfully connected to {credentials["ip"]} using {protocol.upper()}')

def handle_ssh(session):
    """Handle SSH connection."""
    try:
    if session.expect(['Password:', 'continue connecting (yes/no)?', pexpect.TIMEOUT, pexpect.EOF]) == 1:
            session.sendline('yes')
            session.expect('Password:') 
        
        session.sendline(credentials["password"])
        if session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF]) == 0:
            session.sendline('enable')
            if session.expect(['Password:', '#', pexpect.TIMEOUT, pexpect.EOF]) == 0:
                session.sendline(credentials["enable_password"])
                session.expect('#')
        
        logging.info('SSH connection successful')
        configure_device(session, 'ssh')  # Passing 'ssh' protocol to configure_device
    except Exception as e:
        logging.error(f"SSH connection failed: {e}")

def handle_telnet(session):
    """Handle Telnet connection."""
    try:
        session.expect('Username:')
        session.sendline(credentials["username"])
        session.expect('Password:')
        session.sendline(credentials["password"])
        
        if session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF]) == 0:
            session.sendline('enable')
            if session.expect(['Password:', '#', pexpect.TIMEOUT, pexpect.EOF]) == 0:
                session.sendline(credentials["enable_password"])
                session.expect('#')
        
        logging.info('Telnet connection successful')
        configure_device(session, 'telnet')  # Passing 'telnet' protocol to configure_device
    except Exception as e:
        logging.error(f"Telnet connection failed: {e}")

def connect_device(protocol):
    """Connect to the device based on the selected protocol."""
    try:
        if protocol == 'ssh':
            session = pexpect.spawn(f'ssh {credentials["username"]}@{credentials["ip"]}', encoding='utf-8', timeout=30)
                if session.expect(['Password:', 'continue connecting (yes/no)?', pexpect.TIMEOUT, pexpect.EOF]) not in [0, 1]:
                print(f'--- FAILURE! creating SSH session for {credentials["ip"]}. Error: {session.before}')
                logging.error(f"Failed to create SSH session for {credentials['ip']}: {session.before}")
                return
            handle_ssh(session)

        elif protocol == 'telnet':
            session = pexpect.spawn(f'telnet {credentials["ip"]}', encoding='utf-8', timeout=30)
            if session.expect(['Username:', pexpect.TIMEOUT, pexpect.EOF]) != 0:
                print(f'--- FAILURE! creating Telnet session for {credentials["ip"]}. Error: {session.before}')
                logging.error(f"Failed to create Telnet session for {credentials['ip']}: {session.before}")
                return
            handle_telnet(session)
    except Exception as e:
        logging.error(f"Connection attempt failed: {e}")

def interactive_menu():
    """Interactive menu for selecting the protocol and connecting to the device."""
    while True:
        print("\n--- Device Connection Menu ---")
        print("1. Connect using SSH")
        print("2. Connect using Telnet")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            connect_device('ssh')
        elif choice == '2':
            connect_device('telnet')
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            logging.info("Program exited by the user")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
            logging.warning(f"Invalid menu choice: {choice}")

# Call the interactive menu
interactive_menu()
