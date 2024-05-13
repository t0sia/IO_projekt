import numpy as np
from update_signals_xml import update
from get_output import get_output
from subprocess import Popen, PIPE
from os import getcwd, chdir, getenv

from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair


'''
https://www.matsim.org/apidocs/signals/0.9.0/org/matsim/contrib/signals/model/package-summary.html
signal - światło drogowe
signal group - grupa świateł, w której wszystkie światła mają zawsze zgodny kolor
signal system - zbiór grup świateł razem kontrolowanych (np. na jednym skrzyżowaniu)

parametry:
    cycle time - czas trwania jednego cyklu świateł [zał: const]
    onset - sekunda cyklu kiedy zapali się zielone światło
    dropping - sekunda cyklu kiedy zapali się czerwone światło
    amber, offset - nieużywane tutaj

cel: modyfikacja onsetu i droppingu
minimum: jeden system, kilka grup + constrainty
'''

BASE_DIR = '/Users/antoninakus/Desktop/io/IO_projekt/'
SIGNALS = 'custom-scenario/signal_control.xml'
OUTPUT = 'output/equil/equilTestRun/scorestats.txt'
MATSIM = 'java'
JAVA = 'java '
FLAGS = '-jar '
JAR = '../java/matsim-example-project-0.0.1-SNAPSHOT.jar '

class P(ElementwiseProblem): # https://pymoo.org/interface/problem.html
    def __init__(self, n_var, conflicts=[], cycle_time=60):
        super().__init__(
            n_var=n_var,                         # ilość grup x2
            n_obj=1,                             # tylko funkcja f - wynik z matsima
            n_ieq_constr=1+n_var+len(conflicts),
            n_eq_constr=0,
            xl=0,                                # lower bound
            xu=cycle_time,                       # upper bound
            vtype=int,
        )
        self.conflicts = conflicts

    def _evaluate(self, x, out, *args, **kwargs): # x - grupy świateł - [onset1,onset2,...,onsetn,dropping1,dropping2,...,droppingn]
        x = np.insert(x, 0, 0) # złamanie symetrii
        count = len(x)//2
        cycle_time = self.xu[0]
        # step 1: modyfikuj xml config
        # step 2: ewaluuj config
        
        g1 = [10 + x[i] - x[count+i] for i in range(count)] # g2: dropping - onset >= 10 [minimalny czas zielonego światła to 10 sekund]
        g2 = [10 - x[i] - cycle_time + x[count+i] for i in range(count)] # g3: onset + (cycle_time - dropping) >= 10 [minimalny czas czerwonego światła to 10 sekund]
        g3 = [x[count+x2]-x[count+x1] if x[x2]-x[x1]<0 else x[count+x1]-x[count+x2] for (x1,x2) in self.conflicts] # jak konflikt to oba światła nie mogą się naraz świecić
        # h1 = [0]

        update(x, BASE_DIR + SIGNALS)

        ret_dir = getcwd()
        chdir(BASE_DIR + MATSIM)
        Popen(JAVA + FLAGS + JAR, shell=True, stdout=PIPE, stderr=PIPE, env={'PATH': getenv('PATH')}).communicate()
        f = get_output(BASE_DIR + OUTPUT)
        print(f)
        chdir(ret_dir)

        out["F"] = f
        out["G"] = np.row_stack([g1+g2+g3])
        # out["H"] = np.row_stack([h1])

def main(problem, algorithm):
    result = minimize(
        problem,
        algorithm,
        termination=('n_gen', 25),
        seed=1,
        verbose=True,
    )
    
    print("Best solution found: \nX = %s\nF = %s" % (result.X, result.F))
    
    return result
    
if __name__ == "__main__":
    prob = P(
        n_var=12-1,
        conflicts=[(0,1)]
    )
    algo = GA(
        pop_size=5,
        vtype=int,
        eliminate_duplicates=True,
        sampling=IntegerRandomSampling(),
        crossover=SBX(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
        mutation=PM(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
    )

    main(prob, algo)
