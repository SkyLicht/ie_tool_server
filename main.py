from src.programs.logs.target_miss import TargetMissLogs
from src.service.live_hours_update import live_hours_update_run, update_the_day_before


def get_live_hour():
    # Placeholder function for live hour functionality
    live_hours_update_run()


def update_work_plan():
    # Placeholder function for updating work plan
    print("Update Work Plan: Functionality to update work plan goes here.")


def log_event_system():
    # Placeholder function for logging events
    print("Log Event System: Functionality to log events goes here.")


def test_mackenzie_api():
    # Placeholder function for testing Mackenzie API
    print("Test Mackenzie API: Functionality to test Mackenzie API goes here.")


def test_workplan_api():
    # Placeholder function for testing work plan API
    print("Test Work Plan API: Functionality to test work plan API goes here.")


def test_live_hours():
    # Placeholder function for testing live hours
    print("Test Live Hours: Functionality to test live hours goes here.")


def main():
    # TargetMissLogs().execute()
    update_the_day_before()
    while True:
        # Display the main menu options
        print("\nMain Menu:")
        print("1. Live Hour")
        print("2. Update Work Plan")
        print("3. Log Event System")
        print("4. Test Submenu")
        print("5. Exit")

        # Get user choice
        main_choice = input("Enter your choice (1-5): ")

        # Process main menu choice
        if main_choice == "1":
            get_live_hour()
        elif main_choice == "2":
            update_work_plan()
        elif main_choice == "3":
            log_event_system()
        elif main_choice == "4":
            # Display the submenu options
            print("\nSubmenu:")
            print("1. Test Mackenzie API")
            print("2. Test Work Plan API")
            print("3. Test Live Hours")
            print("4. Back to Main Menu")

            # Get user choice from submenu
            submenu_choice = input("Enter your choice (1-4): ")

            # Process submenu choice
            if submenu_choice == "1":
                test_mackenzie_api()
            elif submenu_choice == "2":
                test_workplan_api()
            elif submenu_choice == "3":
                test_live_hours()
            elif submenu_choice == "4":
                continue  # Go back to the main menu
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        elif main_choice == "5":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
    pass


if __name__ == '__main__':
    main()



