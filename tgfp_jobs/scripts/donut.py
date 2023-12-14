# library
import matplotlib.pyplot as plt


def main(team1: Tg):
    # create data
    labels = "49ers", "Cardinals"
    size_of_groups = [72.3, 27.0]

    # Create a donut
    plt.pie(size_of_groups, labels=labels, autopct='%1.1f')

    # add a circle at the center to transform it in a donut chart
    my_circle = plt.Circle((0, 0), 0.85, color='white')
    p = plt.gcf()
    p.gca().add_artist(my_circle)

    plt.savefig('donut.png')
    plt.show()


if __name__ == '__main__':
    main()
