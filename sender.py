from socket import *  #To import all functions of a Socket
from util import create_checksum, make_packet #To import functions from util.py

class Sender:
  def __init__(self):
      """ 
        Your constructor should not expect any argument passed in,
        as an object will be initialized as follows:
        sender = Sender()
        Please check the main.py for a reference of how your function will be called.
      """ 
      #Use UDP connection to create socket AND set the receiver's IP address/Port to connect later
      self.Sender_Socket = socket(AF_INET, SOCK_DGRAM)  
      self.Receiver_Addr = ('127.0.0.1', 10368) 
      self.seq_num = 0        #Initialize sequence number
      self.ack_num = 0        #Initialize acknowledgement number
      self.packet_number = 0  #Initialize Packet number counter
  
  
  #Create sender's packet
  def make_sender_packet(self, app_msg_str, ack_num, seq_num):
     #Create a packet to send to receiver
      packet = make_packet(app_msg_str, ack_num, seq_num)

      #Create a checksum for the packet
      checksum = create_checksum(packet)

      #Subsitute the initial value of checksum b'\x00\x00' with the calculated check sum, in the packet.
      packet = packet[:8] + checksum + packet[10:]   #Ex: b'COMPNETW\xf7\xde\x00@msg1'

      return packet
  

  def rdt_send(self, app_msg_str):
      """realibly send a message to the receiver (MUST-HAVE DO-NOT-CHANGE)
      Args:
        app_msg_str: the message string (to be put in the data field of the packet)
      """
      #Display original message to sender
      print('\n\r\n\roriginal message string: ',app_msg_str)

      #Create a packet to send to receiver
      packet = self.make_sender_packet(app_msg_str, self.ack_num, self.seq_num)
      print('packet created: ',packet)

      while True:
          #Increment packet number for every packet transmitted/restransmitted eg: Num1, Num2, Num3 etc..
          self.packet_number += 1

          #Send the packet to receiver
          self.Sender_Socket.sendto(packet, self.Receiver_Addr)
          print(f"packet num.{self.packet_number} is successfully sent to the receiver.")

          try: #Handle exceptions at Sender side in case of timeout
              
              #Set a timeout of 3 seconds
              self.Sender_Socket.settimeout(3)  

              #Receive ACK packet from receiver
              AckPacket, Addr = self.Sender_Socket.recvfrom(1024)

              #Extract the 15th bit by shifting the 8 bits of the 12th byte to the right by one place (acknowledgment number)
              AckNo_AckPacket = (AckPacket[11] >> 1) & 1

              #Extract the 16th bit from  the 8 bits of the 12th byte -last bit picked by default(sequence number)
              SeqNo_AckPacket = AckPacket[11] & 1

              #Check if ACK sent is for current seq_num or retransmission of packet necessary
              if  AckNo_AckPacket == self.seq_num: 
                print(f"packet is received correctly: seq. num {SeqNo_AckPacket} = ACK num {AckNo_AckPacket}. all done! ")
                
                #Toggle the values for seq number/ack from 0 to 1 or vice versa for the next packet
                self.seq_num = 1 - self.seq_num

                #break from the main loop for transmission of a new packet
                break  

              #explicitly to handle corrupt packets  /restransmit the packet
              else: 

                #Retransmission of the packet is necessary because the ACK does not match with the sequence number
                print('receiver acked the previous pkt, resend!')
                print(f"\n\r\n\r[ACK-Previous retransmission]: {app_msg_str}")

          except timeout:
              #Handle timeout exception (if any)  at the sender's end and display msg to allow restransmission of packet
              print('socket timeout! Resend!')
              print(f"\n\r\n\r[timeout restranmission]: {app_msg_str}")       

  ####### Your Sender class in sender.py MUST have the rdt_send(app_msg_str)  #######
  ####### function, which will be called by an application to                 #######
  ####### send a message. DO NOT change the function name.                    #######                    
  ####### You can have other functions if needed.                             #######   