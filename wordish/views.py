from django.shortcuts import render

# Create your views here.
def start_action(request):
    if request.method == "GET":
        context = {"message": "Welcome to Wordish"}
        return render(request, 'index.html', context)

    try:
        target = _process_param(request, "target_text")
        if not target.isalpha() or len(target) != 5:
            context = {"message": "Invalid input"}
            return render(request, 'index.html', context)
        context = _compute_context(target, [], "Start")
        return render(request, 'wordish.html', context)
    except Exception as e:
        context = {"message": str(e)}
        return render(request, 'index.html', context)

def guess_action(request):
    if request.method == "GET":
        context = {"message": "You're hacking. Try again!"}
        return render(request, 'index.html', context)

    fields = ['guess_text', 'target', 'guesses']
    if not all(field in request.POST for field in fields):
        context = {"message": "You're hacking. Error!"}
        return render(request, 'index.html', context)

    try:
        target = _process_param(request, "target")
        guesses = _process_old_guesses(request)
        if not target.isalpha() or len(target) != 5 or not all(len(word)==5 and word.isalpha() for word in guesses):
            context = {"message": "You're hacking. Error!"}
            return render(request, 'index.html', context)
    except Exception as e:
        return render(request, "index.html", {"message": f"Fatal error: {e}"})

    try:
        new_guess = _process_param(request, "guess_text")
        if not new_guess.isalpha() or len(new_guess) != 5:
            context = _compute_context(target, guesses, "Invalid input")
            return render(request, 'wordish.html', context)
        guesses.append(new_guess)
        if target == new_guess:
            context = _compute_context(target, guesses, "You win!!!")
        elif len(guesses) >= 6:
            context = _compute_context(target, guesses, "Too many tries! You lose!!!")
        else:
            context = _compute_context(target, guesses, "Almost!")
    except Exception as e:
        context = _compute_context(target, guesses, f"Invalid input: {e}")

    return render(request, "wordish.html", context)

def _process_param(request, keyword):
    word = ""
    if request.method == "POST":
        if keyword in request.POST:
            word = request.POST[keyword]
    return word

def _process_old_guesses(request):
    old_guesses = []
    if request.method == "POST":
        if 'guesses' in request.POST:
            guess_str = request.POST['guesses']
            i = 0
            while i < len(guess_str):
                if guess_str[i].isalpha():
                    old_guesses.append(guess_str[i:i+5])
                    i += 5
                else:
                    i += 1
    return old_guesses

def _compute_context(target, guesses, message=""):
    matrix = []
    for row in range(6):
        matrix.append([])
        if len(guesses) > row:
            letter_list = [*guesses[row]]
            color_list = _compute_color(target, guesses[row])
        else:
            letter_list = [""] * 5
            color_list = ["white"] * 5
        for col in range(5):
            cell = {"id": "cell_"+str(row)+"_"+str(col), "letter": letter_list[col], "color": color_list[col]}
            matrix[row].append(cell)
    message = message
    context = {
        "message": message,
        "matrix": matrix,
        "target": target,
        "old_guesses": guesses
    }
    return context

def _compute_color(target, guess):
    not_colored = dict()
    color_list = []
    for i in range(5):
        not_colored[target[i]] = not_colored.get(target[i], 0) + 1
    for i in range(5):
        if target[i] == guess[i]:
            not_colored[guess[i]] -= 1
            color_list.append("green")
        elif guess[i] in target:
            left = not_colored[guess[i]]
            counter = 0
            for j in range(i, 5):
                if guess[j] == guess[i]:
                    if guess[j] == target[j]:
                        counter += 1
            if left > counter:
                not_colored[guess[i]] -= 1
                color_list.append("yellow")
            else:
                color_list.append("gray")
        else:
            color_list.append("gray")
    return color_list



