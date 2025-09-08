import os

import streamlit as st

from config import response_number_to_response

SYMBOL_BLANK = response_number_to_response[" "]


def main():
    mode = st.sidebar.radio("Modo", ["Corrector", "config"])

    if mode == "Corrector":
        page_corrector()
    elif mode == "config":
        page_config()
    else:
        raise NotImplementedError


def page_config():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Registrar nuevo test")
        new_test_name = st.text_input("Nombre del test")
        new_test_responses = st.text_input("Respuestas del test. Usa ABCD. Intro para chequear longitud.")

        if new_test_responses:
            st.text(f'Número de respuestas: {len(new_test_responses)}')

        if st.button("Guardar"):
            if set(new_test_responses) - set("ABCD"):
                st.error("Sólo puedes escribir A, B, C, D")
                st.stop()

            save_test(new_test_name, new_test_responses)
            st.success("Guardado!")

    with col2:
        st.subheader("Chequear test")

        test_name = choose_test(key="check")

        responses_real = load_test(test_name)

        st.text(responses_real)

    with col2:
        st.subheader("Borrar test")

        test_name = choose_test(key="delete")

        if st.button("Borrar"):
            os.remove(f"./data/{test_name}.txt")
            st.success(f"Se borró el test '{test_name}'")


def save_test(test_name, responses):
    if os.path.exists(f"./data/{test_name}.txt"):
        st.info(f"Se sobreescribió el test '{test_name}'")

    with open(f"./data/{test_name}.txt", "w") as f:
        f.write(responses)


def page_corrector():
    st.title("Corrector")

    col1, col2, _ = st.columns(3)
    with col1:
        test_name = choose_test(key="corrector")
    with col2:
        substract_error = choose_substract_error()

    responses_real = load_test(test_name)
    n_questions = len(responses_real)

    responses_student = ask_for_student_responses(n_questions)

    if st.button("Corregir"):
        check_n_responses(responses_student, responses_real)
        show_responses_coloured(responses_student, responses_real)
        n_good, n_bad, n_blanks, errors, mark = calculate_results(responses_student, responses_real, substract_error)
        show_results(n_good, n_bad, n_blanks, errors, mark)


def check_n_responses(responses_student, responses_real):
    if len(responses_real) != len(responses_student):
        st.error(f"Hay {len(responses_student)} respuestas, y el test tiene {len(responses_real)}")
        st.stop()



def show_responses_coloured(responses_student, responses_real):
    colored_responses = [
        f'<span style="color:green">{resp}</span>' if resp == real
        else f'<span style="color:blue">{SYMBOL_BLANK}</span>' if resp == SYMBOL_BLANK
        else f'<span style="color:red">{resp}</span>'
        for resp, real in zip(responses_student, responses_real)
    ]

    st.markdown(' '.join(colored_responses), unsafe_allow_html=True)


def show_results(n_good, n_bad, n_blank, errors, mark):
    col1, col2, _ = st.columns(3)

    with col1:
        st.markdown(f'<span style="color:green; font-weight:bold; font-size:24px">✓ {n_good}</span>', unsafe_allow_html=True)
        st.markdown(f'<span style="color:red; font-weight:bold; font-size:24px">X {n_bad}</span>', unsafe_allow_html=True)
        st.markdown(f'<span style="color:blue; font-weight:bold; font-size:24px">{SYMBOL_BLANK} {n_blank}</span>', unsafe_allow_html=True)

    st.write(f"Errores en preguntas: {', '.join(map(str, errors))}")

    with col2:
        mark = round(mark, 2)
        if mark >= 5:
            st.success(f"Nota: {mark}")
        else:
            st.error(f"Nota: {mark}")


def calculate_results(responses_student, responses_real, substract_error):
    n_blanks = 0
    n_good = 0
    n_bad = 0
    errors = []

    for i, (r_student, r_real) in enumerate(zip(responses_student, responses_real), start=1):
        if r_student == SYMBOL_BLANK:
            n_blanks += 1
        elif r_real == r_student:
            n_good += 1
        else:
            n_bad += 1
            errors.append(i)

    mark = (n_good * 1 - n_bad * substract_error) / len(responses_real) * 10
    if mark < 0:
        mark = 0

    return n_good, n_bad, n_blanks, errors, mark


def ask_for_student_responses(n_questions):
    responses_student_code = st.text_input(
        "Respuestas alumno. Usa A1 B2 C9 D0 y espacio para no contesta. Pulsa Intro para chequear.", max_chars=n_questions,
        autocomplete="off")

    if set(responses_student_code) - set("1290 "):
        st.error(f"Sólo puedes escribir 1, 2, 9, 0 o espacios")
        st.stop()

    responses_student = [response_number_to_response[response] for response in responses_student_code]

    if responses_student:
        responses_student_str = " ".join(responses_student)
        st.text(responses_student_str)

    return responses_student


def choose_test(key):
    tests = [file[:-4] for file in os.listdir("./data") if file.endswith(".txt")]

    test = st.selectbox("Qué test", tests, key=key)

    return test


def choose_substract_error():
    substract_error_str = st.selectbox("Fallar resta _ aciertos: ", ['1/2', '1/3', '1/4'], index=1)

    if substract_error_str == '1/2':
        substract_error = 1/2
    elif substract_error_str == '1/3':
        substract_error = 1/3
    elif substract_error_str == '1/4':
        substract_error = 1/4

    return substract_error


def load_test(test_name):
    with open(f"./data/{test_name}.txt", "r") as f:
        responses_real = f.read()

        return responses_real


if __name__ == "__main__":
    main()
