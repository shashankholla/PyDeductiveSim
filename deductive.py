# Name: Shashank Karkada Holla
# Deductive Fault Simulator
# Usage: Follow the examples in the README.pdf file


from typing import List, Tuple, Dict
import sys
import random, math
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description="Deductive fault simulator")

parser.add_argument("--cktfile", metavar="c", type=str, help="Input the circuit file")
parser.add_argument(
    "--coverage", metavar="cv", type=float, help="Input the circuit file"
)

parser.add_argument("--ip_vectors", metavar="iv", type=str, help="Input vectors")
parser.add_argument("--faultfile", metavar="ff", type=str, help="Faults file")
parser.add_argument("--allfaults", action="store_true", help="All faults")
parser.add_argument("--randomvectors", action="store_true", help="All faults")
parser.add_argument(
    "--repeat", metavar="rr", type=int, help="Repeat N times to get best vectors"
)


args = parser.parse_args()


cktFile = args.cktfile
INPUTS = args.ip_vectors
faultFilePath = args.faultfile

# Gate Class
class Gate:
    def __init__(self, type, i, o):
        self.type = type
        self.i = i
        self.o = o
        self.faultList = []

    def __str__(self):
        return self.type + " " + str(self.i) + " " + str(self.o)

    def __repr__(self):
        return self.__str__()


# Compute Function for circuit simulator
def compute(gate, wires, table):
    if wires.get(gate.o, -1) != -1:
        return wires[gate.o]

    if gate.type == "AND":
        if gate.i[0] in wires:
            a = wires[gate.i[0]]
        else:
            a = compute(table[gate.i[0]], wires, table)
            wires[gate.i[0]] = a
        if gate.i[1] in wires:
            b = wires[gate.i[1]]
        else:
            b = compute(table[gate.i[1]], wires, table)
            wires[gate.i[1]] = b

        return a & b

    if gate.type == "NAND":
        if gate.i[0] in wires:
            a = wires[gate.i[0]]
        else:
            a = compute(table[gate.i[0]], wires, table)
            wires[gate.i[0]] = a
        if gate.i[1] in wires:
            b = wires[gate.i[1]]
        else:
            b = compute(table[gate.i[1]], wires, table)
            wires[gate.i[1]] = b

        return not (a & b)

    if gate.type == "OR":
        if gate.i[0] in wires:
            a = wires[gate.i[0]]
        else:
            a = compute(table[gate.i[0]], wires, table)
            wires[gate.i[0]] = a
        if gate.i[1] in wires:
            b = wires[gate.i[1]]
        else:
            b = compute(table[gate.i[1]], wires, table)
            wires[gate.i[1]] = b

        return a | b

    if gate.type == "NOR":
        if gate.i[0] in wires:
            a = wires[gate.i[0]]

        else:
            a = compute(table[gate.i[0]], wires, table)
            wires[gate.i[0]] = a
        if gate.i[1] in wires:
            b = wires[gate.i[1]]
        else:
            b = compute(table[gate.i[1]], wires, table)
            wires[gate.i[1]] = b

        return not (a | b)

    if gate.type == "INV":
        if gate.i[0] in wires:
            a = wires[gate.i[0]]
        else:
            a = compute(table[gate.i[0]], wires, table)
            wires[gate.i[0]] = a

        return not a

    if gate.type == "BUF":
        if gate.i[0] in wires:
            a = wires[gate.i[0]]
        else:
            a = compute(table[gate.i[0]], wires, table)
            wires[gate.i[0]] = a

        return a


def deduce(gate, faultMap, inputs, wires, table):

    if gate.type in ["AND", "NAND", "OR", "NOR"]:
        if not gate.i[0] in inputs:
            deduce(table[gate.i[0]], faultMap, inputs, wires, table)
        if not gate.i[1] in inputs:
            deduce(table[gate.i[1]], faultMap, inputs, wires, table)

        faultListA = set(faultMap.get(gate.i[0], set()))
        faultListB = set(faultMap.get(gate.i[1], set()))

        ip1 = wires[gate.i[0]]
        ip2 = wires[gate.i[1]]
        if gate.type in ["AND", "NAND"]:
            if ip1 == 0:
                if ip2 == 0:  # A -> 0 , B -> 0
                    faultMap[gate.o] = (
                        set(faultListA)
                        .intersection(set(faultListB))
                        .union(faultMap.get(gate.o, set()))
                    )
                else:  # A -> 0, B -> 1
                    faultMap[gate.o] = (set(faultListA) - set(faultListB)).union(
                        faultMap.get(gate.o, set())
                    )

            if ip1 == 1:
                if ip2 == 0:  # A -> 1 , B -> 0
                    faultMap[gate.o] = (set(faultListB) - set(faultListA)).union(
                        faultMap.get(gate.o, set())
                    )
                else:  # A -> 1, B -> 1
                    faultMap[gate.o] = (
                        set(faultListA)
                        .union(set(faultListB))
                        .union(faultMap.get(gate.o, set()))
                    )

            # return a & b

        if gate.type in ["OR", "NOR"]:
            if ip1 == 0:
                if ip2 == 0:  # A -> 0 , B -> 0
                    faultMap[gate.o] = (
                        set(faultListA)
                        .union(set(faultListB))
                        .union(faultMap.get(gate.o, set()))
                    )
                else:  # A -> 0, B -> 1
                    faultMap[gate.o] = (set(faultListB) - set(faultListA)).union(
                        faultMap.get(gate.o, set())
                    )

            if ip1 == 1:
                if ip2 == 0:  # A -> 1 , B -> 0
                    faultMap[gate.o] = (set(faultListA) - set(faultListB)).union(
                        faultMap.get(gate.o, set())
                    )
                else:  # A -> 1, B -> 1
                    faultMap[gate.o] = (
                        set(faultListA)
                        .intersection(set(faultListB))
                        .union(faultMap.get(gate.o, set()))
                    )

    if gate.type in ["INV", "BUF"]:
        if not gate.i[0] in inputs:
            deduce(table[gate.i[0]], faultMap, inputs, wires, table)
        faultListA = set(faultMap.get(gate.i[0], set()))
        faultMap[gate.o] = faultListA.union(faultMap.get(gate.o, set()))


def faultDeduction(cktFile, cktInput, faultFilePath):
    with open(cktFile, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.split()[0] == "INPUT":
                inpLen = len(line[5:].strip().split()) - 1
                break

        inpVec = cktInput.strip()

        gates: List[Gate] = []
        inputs = []
        outputs = []
        wires = dict()
        table = dict()
        faultMap = dict()
        f.seek(0)
        while True:
            newLine = f.readline()
            if newLine == None:
                break
            newLine = newLine.split()
            if len(newLine) != 0:
                newLine = [newLine[0]] + list(map(int, newLine[1:]))
                if newLine[0] == "INPUT":
                    inputs = newLine[1:-1]
                    for ip in inputs:
                        wires[ip] = int(cktInput[0])
                        cktInput = cktInput[1:]
                elif newLine[0] == "OUTPUT":
                    outputs = newLine[1:-1]

                else:
                    gates.append(Gate(newLine[0], newLine[1:-1], newLine[-1]))
            else:
                break

        for g in gates:
            table[g.o] = g

        opTxt = ""

        for o in outputs:
            wires[o] = compute(table[o], wires, table)
            opTxt += str(int(wires[o]))

        if args.allfaults == False:
            print(f"Good Simulation output {opTxt}")
        
        if (args.allfaults == False) and (args.faultfile == None):
            return [[], []]

        if args.allfaults or (args.faultfile == None):
            for g in gates:
                for i in g.i:
                    if len(faultMap.get(i, [])) == 0:
                        if wires[i] == 0:
                            faultMap[i] = faultMap.get(i, []) + [str(i) + "_" + "1"]
                        else:
                            faultMap[i] = faultMap.get(i, []) + [str(i) + "_" + "0"]

                if len(faultMap.get(g.o, [])) == 0:
                    if wires[g.o] == 0:
                        faultMap[g.o] = faultMap.get(g.o, []) + [str(g.o) + "_" + "1"]
                    else:
                        faultMap[g.o] = faultMap.get(g.o, []) + [str(g.o) + "_" + "0"]

        elif faultFilePath != None:

            faultFile = open(faultFilePath, "r")
            for line in faultFile:

                line = list(map(int, line.split()))
                if wires[line[0]] != line[1]:
                    faultMap[line[0]] = faultMap.get(line[0], []) + [
                        str(line[0]) + "_" + str(line[1])
                    ]
            for i in inputs:
                faultMap[i] = faultMap.get(i, [])

        ll = list(faultMap.keys()).sort()
        # ll.sort()

        for o in outputs:
            deduce(table[o], faultMap, inputs, wires, table)

        allFaults = list()
        for o in outputs:
            allFaults = allFaults + list(faultMap[o])

        allFaults = list(set(allFaults))
        allFaults.sort(key=lambda x: int(x.split("_")[0]))
        return [allFaults, len(wires)]


if __name__ == "__main__":
    inpLen = 0

    with open(cktFile, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.split()[0] == "INPUT":
                inpLen = len(line[5:].strip().split()) - 1
                break

    if args.ip_vectors != None:
        inputVectorFile = open(args.ip_vectors, "r").readlines()

        for inputVector in inputVectorFile:
            faults, len = faultDeduction(cktFile, inputVector, faultFilePath)
            printVector = " ".join(list(inputVector))
            print(f"Circuit: {cktFile}\t Input vector: {printVector}")
            for fault in faults:
                node = fault.split("_")[0]
                stuckat = fault.split("_")[1]
                print(f"{node:>3} stuck at {stuckat}")

    else:

        bestNumberOfVectors = []
        bestCoverageAsVector = []
        bestVectors = []
        minNumOfVectors = 0xFFFFFFFF
        for i in range(200):
            coverage = 0
            detectedFault = set()
            vectors = []
            coverageAsVector = []
            while coverage < args.coverage:
                num = random.randrange(0, math.pow(2, inpLen))
                while bin(num)[2:0] in vectors:
                    num = random.randrange(0, math.pow(2, inpLen))

                thisVector = bin(num)[2:].zfill(inpLen)

                vectors.append(thisVector)

                thisRun, numberOfWires = faultDeduction(cktFile, thisVector, None)
                detectedFault = detectedFault.union(set(thisRun))
                coverage = len(detectedFault) / (2 * numberOfWires)
                coverageAsVector.append(coverage)

            numberOfVectors = list(range(1, len(coverageAsVector) + 1))

            if len(numberOfVectors) < minNumOfVectors:
                bestNumberOfVectors = list(numberOfVectors)
                bestCoverageAsVector = list(coverageAsVector)
                minNumOfVectors = len(numberOfVectors)
                bestVectors = list(vectors)

        plt.plot(bestNumberOfVectors, bestCoverageAsVector)
        plt.xlabel("Test vector number")
        plt.ylabel("Coverage")
        plt.title(cktFile)
        plt.xticks(bestNumberOfVectors)
        print(bestVectors)

        for i in bestNumberOfVectors:
            if bestCoverageAsVector[i - 1] > 0.75:
                plt.axhline(
                    y=bestCoverageAsVector[i - 1], linestyle="dotted", color="r"
                )
                plt.axvline(x=i, linestyle="dotted", label="75% coverage", color="r")
                plt.text(
                    i,
                    bestCoverageAsVector[i - 1] + 0.01,
                    f"{i},{bestCoverageAsVector[i - 1]*100:.2f}%",
                )
                break
        for i in bestNumberOfVectors:
            if bestCoverageAsVector[i - 1] > 0.90:
                plt.axhline(
                    y=bestCoverageAsVector[i - 1], linestyle="dotted", color="g"
                )
                plt.axvline(x=i, linestyle="dotted", label="90% coverage", color="g")
                plt.text(
                    i,
                    bestCoverageAsVector[i - 1] + 0.01,
                    f"{i} - {bestCoverageAsVector[i - 1]*100:.2f}%",
                )

                break
        plt.legend()
        plt.show()
