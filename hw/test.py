def solution(x, y):
    value = 1
    y_increment = 1
    x_increment = 2

    for i in range(0, y-1):
        # print("{} + {}".format(value, y_increment))
        value += y_increment
        y_increment += 1
        x_increment += 1

    for i in range(0, x-1):
        # print("{} + {}".format(value, x_increment))
        value += x_increment
        x_increment += 1

    return str(value)

if __name__ == "__main__":
    # print(solution(1,1))
    # print(solution(1,2))
    # print(solution(1,3))
    # print(solution(1,4))
    # print(solution(1,5))
    # print(solution(1,6))


    # print(solution(1,1))
    # print(solution(2,1))
    # print(solution(3,1))
    # print(solution(4,1))
    # print(solution(5,1))

    # print(solution(2,1))
    # print(solution(2,2))
    # print(solution(2,3))
    # print(solution(2,4))


    print(solution(5,10))
    # print(solution(2,2))
    # print(solution(2,3))
    # print(solution(2,4))

    # print(solution(2,2))