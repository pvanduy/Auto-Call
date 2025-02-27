import time
import GSM_keys as cmd
import serial
import pygame

#                                                               +----------------------+       +-------------------------+
#                                                               | 5V               Vcc | <---> | 2 *                  5V |
#                                                               |                      |       |                         |
#                                                               |                  GND | <---> | 6                   GND |
#                                                               |                      |       |                         |
#                                                               |      SIM800C     TXD | <---> | 10       Pi GPIO     RX |
#                                                               |                      |       |                         |
#                                                               |                  RXD | <---> | 8                    TX |
#                                                               |                      |       |                         |
#                                                               |                  MCP | <---> | **                  AUX |
#                                                               |                      |       |                         |
#                                                               |                  MCN | <---> | **                  AUX |
#                                                               +----------------------+       +-------------------------+

#BUSY #không nghe máy
#ERROR  
#NO CARRIER có nghe máy xong rồi tắt
#1,0,6,0,0 máy bận

def SIM800(command, ser=None):
    AT_command = command + "\r\n"
    ser.write(str(AT_command).encode('ascii'))
    time.sleep(1)
    if ser.inWaiting() > 0:
        echo = ser.readline() #waste the echo
        response_byte = ser.readline()
        response_str = response_byte.decode('ascii')
        return (response_str)
    else:
        return ("ERROR")

def wait_for_SIM800(ser=None):
    echo = ser.readline()  # waste the echo
    response_byte = ser.readline()
    response_str = response_byte.decode('ascii')
    return (response_str)

def Init_GSM(SERIAL=None):
    if "OK" in SIM800("AT", SERIAL):
        if ("OK" in (SIM800("AT+CLCC=1", SERIAL))) and ("OK" in (SIM800("AT+DDET=1", SERIAL))) and ("OK" in (SIM800("AT+CNMI =0,0,0,0,0", SERIAL))) and ("OK" in (SIM800("AT+CMGF=1", SERIAL))) and ("OK" in (SIM800("AT+CSMP=17,167,0,0", SERIAL))):  # enble DTMF / disable notifications
            print("Everything is ready")
            return True
    else:
        print("------->ERROR -> Module not found")
        return False

def action_incoming_call(SERIAL=None):
    SERIAL.flushInput()
    time.sleep(0.5)
    dtmf_response = "start_over"
    while dtmf_response == "start_over":
        play_mp3(file_name='intro.wav',start=True)
        time.sleep(1)
        dtmf_response = wait_for_SIM800(SERIAL)
        SERIAL.timeout = 15
        if "+DTMF: 1" in dtmf_response:
            SERIAL.timeout = 3
            response = "1"
            play_mp3(file_name='intro.wav',stop=True)
            play_mp3(file_name='thank.wav',start=True)
            while True:
                if not (pygame.mixer.music.get_busy()):
                    play_mp3(file_name='thank.wav',stop=True)
                    hang = SIM800("ATH",SERIAL)
                    break
            break
        if "+DTMF: 2" in dtmf_response:
            SERIAL.timeout = 3
            response = "2"
            play_mp3(file_name='intro.wav',stop=True)
            play_mp3(file_name='thank.wav',start=True)
            while True:
                if not (pygame.mixer.music.get_busy()):
                    play_mp3(file_name='thank.wav',stop=True)
                    hang = SIM800("ATH", SERIAL)
                    break
            break
        if "+DTMF: 3" in dtmf_response:
            response = "3"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 4" in dtmf_response:
            response = "4"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 5" in dtmf_response:
            response = "5"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 6" in dtmf_response:
            response = "6"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 7" in dtmf_response:
            response = "7"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 8" in dtmf_response:
            response = "8"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 9" in dtmf_response:
            response = "9"
            hang = SIM800("ATH", SERIAL)
            break
        if "+DTMF: 0" in dtmf_response:
            play_mp3(file_name='intro.wav',stop=True)
            play_mp3(file_name='intro.wav',start=True)
            dtmf_response = "start_over"
            continue
        if "+DTMF: " in dtmf_response:
            dtmf_response = "start_over"
            continue
        else:
            play_mp3(file_name='intro.wav',stop=True)
            hang = SIM800("ATH", SERIAL)
            response = "REJECTED_AFTER_ANSWERING"
            break

    return response

def Call_response_for (phone_number, ser=None):
    AT_call = "ATD" + phone_number + ";"
    time.sleep(1)
    ser.flushInput() #clear serial data in buffer if any
    if ("OK" in (SIM800(AT_call, ser))) and (",2," in (wait_for_SIM800(ser))) and (",3," in (wait_for_SIM800(ser))):
        print("RINGING...->", phone_number)
        call_status = wait_for_SIM800(ser)
        if "1,0,0,0,0" in call_status:
            print("**ANSWERED**")
            response=action_incoming_call(ser)
        else:
            print("REJECTED")
            response = "CALL_REJECTED"
            hang = SIM800("ATH", ser)
            time.sleep(1)
            ser.flushInput()
    else:
        print("NOT_REACHABLE")
        response = "NOT_REACHABLE"
        hang = SIM800("ATH", ser)
        time.sleep(1)
        ser.flushInput()

    ser.flushInput()
    return (response)

#Receives the message and phone number and send that message to that phone number
def send_message(message, recipient, ser=None):
    ser.write(b'AT+CMGS="' + recipient.encode() + b'"\r')
    time.sleep(0.5)
    ser.write(message.encode() + b"\r")
    time.sleep(0.5)
    ser.write(bytes([26]))
    time.sleep(0.5)
    print ("Message sent to customer")
    time.sleep(2)
    ser.flushInput()  # clear serial data in buffer if any
    
def play_mp3(file_name,start=False,stop=False):
    if start:
        pygame.mixer.init()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
    if stop:
        pygame.mixer.music.stop()

def incoming_phone_call(ser=None):
    ser.flushInput()
    time.sleep(0.5)
    check_incoming = SIM800("AT+CLCC", ser)
    while ser.in_waiting:
        if "+CLCC" in check_incoming:
            cus_phone = check_incoming[18:28]
            ser.flushInput()
            time.sleep(1)
            SIM800("ATA", ser)
            response = action_incoming_call(ser)
            return [cus_phone, response]
        
        else:
            print("Nope its something else")
            return "0"


def start_call(cus_phone):
    ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=15)  # timeout affects call duration and waiting for response currently 30sec
    Init_GSM(ser)
    response = Call_response_for(cus_phone, ser) #place a call and get response from customer
    print ("Response from customer => ", response)
    ser.close()
    time.sleep (5)
    return response

#cus_phone = '+8482789***'
# ser = serial.Serial("COM7", baudrate=9600, timeout=15)  # timeout affects call duration and waiting for response currently 30sec
#print(start_call(cus_phone))
# ser.close()
