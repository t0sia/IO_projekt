def get_output(file='/Users/antoninakus/Desktop/io/IO_projekt/output/scorestats.txt'):
    with open(file, 'r') as f:
        lines = [line for line in f.readlines()]
        score = lines[-1].split('\t')[1]
    
    return score

if __name__ == "__main__":
    get_output()