from utils import Instance



if __name__ == '__main__':
    grade = 0
    for instanceId,threshold in zip(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'],
                                    [0.39, 0.51, 0.44, 0.375, 0.43, 0.54, 0.78, 0.84, 0.85, 0.92, 0.84, 0.95, 0.87, 0.86, 0.82]):
        try:
            inst = Instance(f'./instances/instance{instanceId}.txt')
            try:
                sol = inst.read_solution(f'./solutions/instance{instanceId}.txt')
                value,validity = inst.solution_value_and_validity(sol)
                if validity:
                    if value >= threshold:
                        print(f'instance{instanceId} : ',0.5,'/0.5')
                        grade += 0.5
                    else:
                        print(f'instance{instanceId} : ',0,'/0.5 (threshold has not been met)')
                else:
                    print(f'instance{instanceId} : ',0,'/0.5 (solution invalid)')
            except FileNotFoundError as _:
                print(f'instance{instanceId} : ',0,f'/0.5 (file ./solutions/instance{instanceId}.txt not found)')
                grade+=0
        except FileNotFoundError as _:
            print(f'instance{instanceId} : ',0,f'/0.5 (file ./instances/instance{instanceId}.txt not found)')
            grade+=0
    print('Total ',round(grade,2),'/7.5')
