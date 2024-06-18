def create_checksum(packet_wo_checksum):
    """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)
    Args:
      packet_wo_checksum: the packet byte data (including headers except for checksum field)
    Returns:
      the checksum in bytes
    """
    checksum = 0

    #Length of a packet
    packet_length = len(packet_wo_checksum)

    #Checksum is calculated in 16-bit blocks- the loop iterates through the packet in 2-byte chunks (16 bits)
    for i in range(0, packet_length , 2): 
        data = packet_wo_checksum[i:i + 2]

        #Convert the 16-bit data block into an integer #Ex:133151, for the first packet containing data 'msg1', seq =0 and ack = 0
        checksum += int.from_bytes(data, byteorder='big')  

    #Shifts the checksum value right by 16 bits, effectively isolating any carry bits.
    checksum_shift16 = checksum >> 16 #Ex: 2

    #'& 0xFFFF' In binary,it is represented as '1111111111111111', ensuring that the checksum fits as a 16-bit value.
    checksum_0xFFFF = checksum & 0xFFFF #Ex: 2079 

    #The integer values obtained in the previous steps are added together
    #carry bits (if any) that exceed 16 bits are effectively wrapped around by addition, ensuring that the checksum is within the 16-bit limit.
    checksum = checksum_shift16 + checksum_0xFFFF  #Ex: 2081

    #calculate the one's complement-inverts all the bits in the 16-bit value. 
    #0xFFFF is used to ensure that the result of one's complement stays within the 16 bit limit
    checksum = ~checksum & 0xFFFF  #Ex: 63454

    #convert the 16-bit checksum back into a bytes object
    checksum = checksum.to_bytes(2, byteorder='big') #eg: b'\xf7\xde' 

    return checksum

   
def verify_checksum(packet):
    """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)
    Args:
      packet: the whole (including original checksum) packet byte data
    Returns:
      True if the packet checksum is the same as specified in the checksum field
      False otherwise
    """
    #Extract the checksum from the packet
    ReceivedChecksum = packet[8:10]

    #Calculate a new checksum by replacing the existing checksum in the packet with initial values b'\x00\x00'
    NewChecksum = create_checksum(packet[:8] + b'\x00\x00' + packet[10:])
    
    #Same checksum means no bit errors; Else consider packet error
    if ReceivedChecksum == NewChecksum: 
        status = True
    else:
        status = False

    return status


def make_packet(data_str, ack_num, seq_num):
    """Make a packet (MUST-HAVE DO-NOT-CHANGE)
    Args:
      data_str: the string of the data (to be put in the Data area)
      ack: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
      seq_num: an int tells the sequence number, i.e., 0 or 1
    Returns:
      a created packet in bytes
    """
    # make sure your packet follows the required format!

    header = 'COMPNETW'     #8 bytes
    checksum = '\x00\x00'   #initial value before the real checksum is calculated

    #Calculate the packet length
    #Length of data + 8 bytes of 'COMPNETW'+ 2 bytes checksum+ 2 bytes of (length field 14 bits + ack 1 bit + seq 1 bit)
    packet_length = len(data_str) + 12  

    #Combine packet_length, ack, and seq into a single 2-byte value by shifting bits
    packet_length_ackseq = (packet_length << 2) | (ack_num << 1) | seq_num

    #Convert the combined value from int to bytes in big-endian order (2 bytes) eg: \x00@ for ack=0; seq=0
    packet_length = packet_length_ackseq.to_bytes(2, byteorder='big') 

    #encode() is typically used to convert a string into bytes using character encoding 
    #Create the final packet eg: b'COMPNETW\x00\x00\x00@msg1'
    packet = header.encode() + checksum.encode() + packet_length + data_str.encode()

    return packet

###### These three functions will be automatically tested while grading. ######
###### Hence, your implementation should NOT make any changes to         ######
###### the above function names and args list.                           ######
###### You can have other helper functions if needed.                    ######  
