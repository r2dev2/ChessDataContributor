def progressBar(percentage: float) -> str:
    numpound = round(percentage*40)
    numdash = 40-numpound
    return '[' + numpound*'#' + numdash*'-' + ']\t' + "%.2f" % (percentage*100) + "%"

def countOutput(count: int, length: int) -> None:
    print(progressBar(count/length), end='\r', flush=True)