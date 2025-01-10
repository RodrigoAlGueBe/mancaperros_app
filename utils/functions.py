def f_unit_type_finder(reps):
    """
    Función que retorna el tipo de unidad de medida en un ejercicio a través de sus repeticiones.
    i.e. Si las repeticiones son 10, entonces la unidad de medida es integer, pero si las repeticiones
    son 10s, entonces la unidad de medida es temporal y en segundos en este caso.

    :param reps: repeticiones del ejercicio (str)
    :return: tipo de unidad de medida (str)
    """
    if 's' in reps:
        return 'time (seconds)'
    elif 'm' in reps:
        return 'time (minutes)'
    else:
        return 'integer'
    

def f_time_reps_to_reps_equivalence(time_rep):
    """
    Función que convierte las repeticiones de tiempo a repeticiones equivalentes en integer.
    Esta función utiliza fibonacci para calcular las repeticiones equivalentes, de forma que
    10 segundos sería equivalente a 2 repeticiones.

    :param time_rep: repeticiones de tiempo (str)
    :return: repeticiones equivalentes en integer (str)
    """
    if 's' in time_rep:
        time_rep = int(time_rep[:-1])
        return str(fibonacci(time_rep))
    elif 'm' in time_rep:
        time_rep = int(time_rep[:-1])
        return str(fibonacci(time_rep * 60))
    else:
        return time_rep
    

def fibonacci(n):
    """
    Función que retorna el n-ésimo número de Fibonacci.

    :param n: posición en la secuencia de Fibonacci (int)
    :return: n-ésimo número de Fibonacci (int)
    """
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def f_reps_to_seconds(time_reps):
    """
    Función que convierte las repeticiones de tiempo (ya sea en minutos o segundos) a segundos.

    :param time_reps: repeticiones de tiempo (str)
    :return: repeticiones en segundos (int)
    """
    if 's' in time_reps:
        return int(time_reps[:-1])
    elif 'm' in time_reps:
        return int(time_reps[:-1]) * 60
    else:
        return int(time_reps)