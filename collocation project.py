import json
import os
import random


FILE_NAME = "data.json"

# -----------------------------
# Đọc dữ liệu
# -----------------------------
def load_data():

    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, "r", encoding="utf-8") as file:
        return json.load(file)


# -----------------------------
# Lưu dữ liệu
# -----------------------------
def save_data(data):

    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# -----------------------------
# Menu
# -----------------------------
def menu():

    print("\n==============================")
    print("      VOCAB TRAINER")
    print("==============================")
    print("1. Thêm collocation")
    print("2. Học collocation")
    print("3. Xem thống kê")
    print("4. Xem toàn bộ collocation")
    print("5. Thoát")


# -----------------------------
# Chương trình chính
# -----------------------------
data = load_data()

while True:

    menu()

    choice = input("Chọn: ")

    if choice == "1":

        english = input("\nNhập collocation: ").strip()

        if english == "":
            print("Không được để trống.")
            continue

        if english in data:
            print("Collocation đã tồn tại.")
            continue

        meaning = input("Nhập nghĩa: ").strip()

        if meaning == "":
            print("Không được để trống.")
            continue

        data[english] = {
            "meaning": meaning,
            "correct": 0,
            "wrong": 0
        }

        save_data(data)

        print("✔ Đã thêm thành công!")


    elif choice == "2":

        if len(data) == 0:
            print("Chưa có collocation nào.")

            continue

        print("\n1. Học tất cả")
        print("2. Chỉ học từ từng sai")

        mode = input("Chọn: ")

        questions = []
        weighted_questions = []

        for english in questions:

            wrong = data[english]["wrong"]

            weighted_questions.append(english)

            for i in range(wrong):
                weighted_questions.append(english)

        questions = weighted_questions

        random.shuffle(questions)

        if mode == "1":

            questions = list(data.keys())

        elif mode == "2":

            for english in data:

                if data[english]["wrong"] > 0:
                    questions.append(english)

            if len(questions) == 0:
                print("🎉 Bạn chưa có từ nào sai.")
                continue

        else:

            print("Lựa chọn không hợp lệ.")
            continue

        random.shuffle(questions)

        correct_count = 0

        wrong_count = 0

        for english in questions:

            print("\n--------------------------------")

            print("Collocation:")

            print(english)

            answer = input("Nghĩa (gõ exit để dừng): ").strip()

            if answer.lower() == "exit":
                break

            if answer.lower() == data[english]["meaning"].lower():

                print("✅ Chính xác!")

                data[english]["correct"] += 1

                correct_count += 1


            else:

                print("❌ Sai!")

                print("Đáp án:", data[english]["meaning"])

                data[english]["wrong"] += 1

                wrong_count += 1

            save_data(data)

        print("\n========== KẾT QUẢ ==========")

        print("Đúng :", correct_count)

        print("Sai  :", wrong_count)

        total = correct_count + wrong_count

        if total > 0:
            accuracy = correct_count / total * 100

            print(f"Accuracy: {accuracy:.2f}%")


    elif choice == "3":

        if len(data) == 0:
            print("Chưa có collocation nào.")

            continue

        total_words = len(data)

        total_correct = 0

        total_wrong = 0

        print("\n========== THỐNG KÊ ==========")

        for english in data:
            total_correct += data[english]["correct"]

            total_wrong += data[english]["wrong"]

        print(f"Tổng collocation : {total_words}")

        print(f"Tổng đúng        : {total_correct}")

        print(f"Tổng sai         : {total_wrong}")

        if total_correct + total_wrong > 0:

            accuracy = total_correct / (total_correct + total_wrong) * 100

            print(f"Accuracy         : {accuracy:.2f}%")


        else:

            print("Accuracy         : Chưa có dữ liệu")

        print("\n===== TOP 5 TỪ SAI NHIỀU NHẤT =====")

        ranking = sorted(

            data.items(),

            key=lambda item: item[1]["wrong"],

            reverse=True

        )

        for i, (english, info) in enumerate(ranking[:5], start=1):
            print(f"{i}. {english}")

            print(f"   Nghĩa : {info['meaning']}")

            print(f"   Đúng  : {info['correct']}")

            print(f"   Sai   : {info['wrong']}")


    elif choice == "4":

        if len(data) == 0:

            print("Chưa có collocation.")


        else:

            print("\n===== DANH SÁCH =====")

            for english in sorted(data.keys()):
                print(f"{english}  -->  {data[english]['meaning']}")

    elif choice == "5":

        save_data(data)

        print("Đã lưu dữ liệu.")

        print("Tạm biệt!")

        break

