from socket import *        #To import all functions of a Socket
from time import sleep      #To import sleep() function to trigger sender's socket timeout
from util import verify_checksum, make_packet, create_checksum
## No other imports allowed

#Create ACK packet
def make_ack_packet(ack_num_packet, seq_num_packet):
    #Create ACK packet
    AckPacket = make_packet('', ack_num_packet, seq_num_packet)
    
    #Create checksum for ACK packet
    AckCheckSum = create_checksum(AckPacket)
    
    #Subsitute the initial value of checksum b'\x00\x00' with the calculated check sum, in the ACK packet.
    AckPacket = AckPacket[:8] + AckCheckSum + AckPacket[10:]  #Ex: b'COMPNETW\xf7\xde\x00@msg1'

    return AckPacket


#Write the received packet into a text file (append)
def write_file(packet):

    #Convert the byte packet to its string representation
    packet_str = repr(packet)
    
    #Text file name
    file_name = 'received_pkt.txt'  

    #Write the received packet into the text file (append) in current working directory
    try:
        with open(file_name, 'a') as file:
            file.write(packet_str + '\n')

    except Exception as e:
        print(f"An error occurred: {e}")
    
   

def rdt_receive(ReceiverSocket, packet_number, expected_seq_num):
    while True:
        #Increment packet number for every packet received eg: Num1, Num2, Num3 etc..
        packet_number += 1

        #Variable to explicitly handle Receiver to sleep to trigger the sender's socket Timeout exception
        sleepTimeout = False

        #Receive the sender's packet
        SenderPacket, Addr = ReceiverSocket.recvfrom(1024)

        print(f"\n\r\n\rpacket num.{packet_number} received: {SenderPacket}" )
        
        #Write all the received packets in received_pkt.txt in the same working directory
        write_file(SenderPacket)

        try:
            #Simulate a delay for packets whose packet number is divisible by 6
            if packet_number % 2 == 0 and packet_number % 3 == 0:
                sleepTimeout = True
                print('simulating packet loss: sleep a while to trigger timeout event on the send side...\n\rall done for this packet!')
                #Sleep for 0.5 seconds to trigger a timeout on the sender side
                sleep(0.5) 
            
            #Extract the 15th bit (ACK) by shifting the 8 bits of the 12th byte to the right by one place
            ack_num_packet = (SenderPacket[11] >> 1) & 1

            #Extract the 16th bit (SEQ) from  the 8 bits of the 12th byte -last bit picked by default
            seq_num_packet = SenderPacket[11] & 1
            
            #Note: SenderPacket[11] retrieves the 12th byte of the received packet containing 'Length , ACK , Sequence number'
            #& 1 is a bitwise AND operation with the value 1. This operation extracts the least significant bit (LSB) of the 12th byte.
            #If LSB of the binary num is 1, the result of binary_number with & 1 will be 1; If LSB is 0, the result is  0.

            #Verify if the packet is corrupt
            IsCheckSumVerified = verify_checksum(SenderPacket)

            #If packet is not corrupt and the received sequence number is as expected and no delay caused by the receiver
            if IsCheckSumVerified == True and expected_seq_num == seq_num_packet and sleepTimeout == False:
                
                #Explicity coded - packets which are NOT divisible by 3 are considered to be NOT CORRUPT
                if packet_number % 3 != 0: 
                    ack_num_packet = seq_num_packet

                    #Create ACK packet
                    AckPacket = make_ack_packet(ack_num_packet, seq_num_packet)

                    #Send the acknowledgment packet to the sender socket's address
                    ReceiverSocket.sendto(AckPacket, Addr)
                    print('packet is expected, message string delivered: ', SenderPacket[12:].decode())
                    print('packet is delivered, now creating and sending the ACK packet...\n\rall done for this packet!')

                    #Toggle the values for expected seq number from 0 to 1 or vice versa for the next incoming packet
                    expected_seq_num = 1 - expected_seq_num

                else: #corrupt packet -explicity coded for packets which are divisible by 3
                    print('simulating packet bit errors/corrupted: ACK the previous packet!\n\rall done for this packet!')
                    
                    #Toggle the values for ack number from 0 to 1 or vice versa for the error packet
                    #This is to acknowledge the previous packet incase of bit errors
                    ack_num_packet = 1 - seq_num_packet

                    #Create ACK packet
                    AckPacket = make_ack_packet(ack_num_packet, seq_num_packet)
                    
                    #Send the ACK packet to the sender
                    ReceiverSocket.sendto(AckPacket, Addr)

        except timeout:
            #Handle timeout exception (if any)  at the receiver's end
            print('Receiver timeout!')


def main():

    #Create receiver socket 
    ReceiverSocket = socket(AF_INET, SOCK_DGRAM)

    #Assign IP and port number
    ReceiverAddr = ('127.0.0.1', 10368) 

    #Bind the socket with IP and port number 
    ReceiverSocket.bind(ReceiverAddr)

    packet_number = 0       #Initialize packet number
    expected_seq_num = 0    #Initialize sequence number of the expected packet

    #Receive packet from sender
    rdt_receive(ReceiverSocket, packet_number, expected_seq_num)

   
#Call main method
if __name__== "__main__":
    main()

    