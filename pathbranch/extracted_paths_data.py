variables = ['x', 'y', 'z', 'choice', 'door_switch', 'car_door', 'host_door']

domain = {
    'x': [1, 2, 3],
    'y': [1, 2, 3],
    'z': [1, 2, 3],
    'choice': [1, 2, 3],
    'door_switch': [1],
    'car_door': [1, 2, 3],
    'host_door': [1, 2, 3]
}

# Example extracted path
extracted_paths4 = [
    [('x > 1', 'True'), ('x > 2', 'False'), ('Statements', ['return 1'])]
]

extracted_paths6 = [

    [('choice == car_door', 'True'), ('Statements', ['return not door_switch'])],
[('choice == car_door', 'False'), ('Statements', ['pass'])],
[('choice != 1 and car_door != 1', 'True'), ('Statements', ['host_door = 1'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'True'), ('Statements', ['host_door = 2'])]
,[('choice != 1 and car_door != 1', 'False'), ('choice != 2 and car_door != 2', 'False'), ('Statements', ['host_door = 3'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'False'), ('Statements', ['choice = 2']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'True'), ('choice == 2', 'False'), ('Statements', ['choice = 2']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'True'), ('Statements', ['choice = 3']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'True'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'True'), ('Statements', ['choice = 2']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'True'), ('Statements', ['choice = 2']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'True'), ('Statements', ['return 1'])]
,[('door_switch', 'True'), ('host_door == 1', 'False'), ('host_door == 2', 'False'), ('choice == 1', 'False'), ('Statements', ['choice = 1']), ('choice == car_door', 'False'), ('Statements', ['pass'])]
,[('door_switch', 'False'), ('Statements', ['pass'])]
]

