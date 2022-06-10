import argparse
from multiprocessing import Pool
import sys

#Main driver
def main():
    print("Project :: R11579832")

    #Take command line arguments and initialize pool data
    args = verifyArgs()
    processPool = Pool(processes=args.threads)
    poolData = fillPoolData(args.inputFile, args.threads)

    #run 100 times and change first and last rows per chunk to updated matrix
    i = 0
    while i < 100:
        poolData = processPool.map(stepCalculator, poolData)
        for chunk in range(len(poolData)):
            poolData[chunk][0] = poolData[chunk-1][-2]
            poolData[chunk][-1] = poolData[(chunk+1) % len(poolData)][1]
        i += 1

    #print to output file
    writeFile(args.outputFile, poolData)

def verifyArgs():
    parser = argparse.ArgumentParser(description = "final project")

    parser.add_argument('-i', action="store", dest="inputFile", required=True)
    parser.add_argument('-o', action="store", dest="outputFile", required=True)
    parser.add_argument('-t', action="store", dest="threads", type=int, default=1)

    return parser.parse_args()

def fillPoolData(input_file, thread_num):
    #file handling
    try:
        with open(input_file, "r") as file:
            file_lines = file.readlines()
    except IOError:
        print("Cannot open", input_file)
        sys.exit(1)

    #This whole chunk of code rewrites the file so each char is encapsulated in an individual list to make it easily changed
    #Also checks file for validity - Cannot have anything but '.'s, 'O's, and newline characters
    lines_list = list()
    chunks = list()
    for line in file_lines:
        lines = list()
        for char in line:
            if not ((char == '.') or (char == 'O') or (char == '\n')):
                print("Invalid file: File must contain only '.', 'O', and newline characters")
                sys.exit(1)
            #Strip newline characters to only store '.'s and 'O's
            if not (char == '\n'):
                chars = [char]
                lines.append(chars)
                del (chars)
        lines_list.append(lines)
        del (lines)

    del (file_lines)

    #Create each chunk to return a list of chunks
    #Each chunk needs to be divided into 'equal' segments which is controlled by "chunk_size" and "count"
    #Append last row in previous chunk to beginning of current chunk and first row in next chunk to end of current chunk
    #
    #"count" is how many chunks will have an extra row
    count = len(lines_list) % thread_num
    #num is a placeholder
    num = 0
    if count > 0:
        chunk_size = len(lines_list) // thread_num + 1
        for i in range(0, chunk_size*(count-1)+1, chunk_size):
            chunk = list()
            for j in range(-1, chunk_size+1):
                chunk.append(lines_list[i+j])
            chunks.append(chunk)
            del (chunk)
            num = i + chunk_size
    chunk_size =  len(lines_list) // thread_num
    #if not count > 0 then num is 0, otherwise num holds the index of the next row to look at
    for i in range(num, len(lines_list), chunk_size):
        chunk = list()
        for j in range(-1, chunk_size+1):
            if not((i + j) == len(lines_list)):
                chunk.append(lines_list[i+j])
            else:
                chunk.append(lines_list[0])
        chunks.append(chunk)
        del (chunk)

    return chunks

def stepCalculator(chunkData):
    chunk = [chunkData[0]]
    for i in range(1, len(chunkData)-1):
        row = list()
        count = 0
        for char in chunkData[i]:
            #list containing values of neighboring cells
            #need the % operator to avoid index out of bounds
            neighbors = [chunkData[i-1][count-1],
                         chunkData[i-1][count],
                         chunkData[i-1][(count+1) % len(chunkData[i])],
                         chunkData[i][count-1],
                         chunkData[i][(count+1) % len(chunkData[i])],
                         chunkData[i+1][count-1],
                         chunkData[i+1][count],
                         chunkData[i+1][(count+1) % len(chunkData[i])]]
            #matrix operation rules
            #need to store new values in a seperate list to avoid incorrect calculations
            count_Os = 0
            for c in neighbors:
                if c[0] == 'O':
                    count_Os += 1
            if char[0] == '.':
                if (count_Os == 2) or (count_Os == 4) or (count_Os == 6) or (count_Os == 8):
                    char = ['O']
            elif char[0] == 'O':
                if not ((count_Os == 2) or (count_Os == 3) or (count_Os == 4)):
                    char = ['.']
            row.append(char)
            del (char)
            del (neighbors)
            count += 1
        chunk.append(row)
        del (row)

    chunk.append(chunkData[-1])
    del (chunkData)
    return chunk

def writeFile(output_file, final_chunks):
    #file handling and print to output file
    try:
        with open(output_file, "w") as file:
            outString = ""
            for chunk in final_chunks:
                for line in range(1, len(chunk)-1):
                    for char in chunk[line]:
                        outString += "".join(char)
                    outString += "\n"

            file.write(outString)
    except IOError:
        print("Path to", output_file, "Does not exist")
        sys.exit(1)

#safe call to main
if __name__ == "__main__":
    main()