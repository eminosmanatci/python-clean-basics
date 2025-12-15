"""
Clean Code Basics - User Management System
Focus: Type hints, error handling, clean structure
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class User:
    """User data model with type hints"""
    id: int
    name: str
    email: str
    active: bool = True
    
    def to_dict(self) -> Dict:
        """Convert User object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "active": self.active
        }


class UserManager:
    """Manages user operations with clean error handling"""
    
    def __init__(self, filename: str = "users.json"):
        self.filename = filename
        self.users = self._load_users()
        logger.info(f"UserManager initialized with {len(self.users)} users")
    
    def _load_users(self) -> List[Dict]:
        """Safely load users from JSON file"""
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                logger.info(f"Loaded users from {self.filename}")
                return data
        except FileNotFoundError:
            logger.warning(f"File {self.filename} not found, starting with empty list")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.filename}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading users: {e}")
            return []
    
    def _save_users(self) -> bool:
        """Save users to JSON file with error handling"""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.users, file, indent=2)
            logger.info(f"Saved {len(self.users)} users to {self.filename}")
            return True
        except IOError as e:
            logger.error(f"Error saving to {self.filename}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving users: {e}")
            return False
    
    def add_user(self, name: str, email: str) -> Optional[User]:
        """Add a new user with validation"""
        try:
            # Input validation
            if not name or not email:
                logger.warning("Attempted to add user with empty name or email")
                return None
            
            if "@" not in email:
                logger.warning(f"Invalid email format: {email}")
                return None
            
            # Check for duplicate email
            for user in self.users:
                if user.get("email") == email:
                    logger.warning(f"Email {email} already exists")
                    return None
            
            # Create new user
            new_id = max([user.get("id", 0) for user in self.users], default=0) + 1
            user = User(id=new_id, name=name, email=email)
            
            # Add to list and save
            self.users.append(user.to_dict())
            success = self._save_users()
            
            if success:
                logger.info(f"Added user: {name} ({email})")
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error adding user {name}: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            for user in self.users:
                if user.get("id") == user_id:
                    return user
            logger.warning(f"User with ID {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def list_users(self, active_only: bool = True) -> List[Dict]:
        """List users with optional filtering"""
        try:
            if active_only:
                return [user for user in self.users if user.get("active", True)]
            return self.users
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID (soft delete)"""
        try:
            for i, user in enumerate(self.users):
                if user.get("id") == user_id:
                    # Soft delete instead of removing
                    self.users[i]["active"] = False
                    success = self._save_users()
                    
                    if success:
                        logger.info(f"Soft deleted user ID {user_id}")
                        return True
                    return False
            
            logger.warning(f"User ID {user_id} not found for deletion")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False


def display_menu():
    """Display command line menu"""
    print("\n" + "="*50)
    print("USER MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Add User")
    print("2. List Users")
    print("3. Get User Details")
    print("4. Delete User")
    print("5. Exit")
    print("="*50)


def main():
    """Main application entry point"""
    manager = UserManager()
    
    print("🚀 Welcome to Clean Code User Management System!")
    print("Type hints, error handling, and clean structure in action.\n")
    
    while True:
        display_menu()
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                # Add User
                print("\n--- ADD USER ---")
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                
                user = manager.add_user(name, email)
                if user:
                    print(f"✅ User added successfully! ID: {user.id}")
                else:
                    print("❌ Failed to add user. Check logs for details.")
            
            elif choice == "2":
                # List Users
                print("\n--- ALL USERS ---")
                users = manager.list_users(active_only=False)
                
                if not users:
                    print("No users found.")
                else:
                    for user in users:
                        status = "✅ Active" if user.get("active", True) else "❌ Inactive"
                        print(f"ID: {user['id']} | Name: {user['name']} | Email: {user['email']} | {status}")
            
            elif choice == "3":
                # Get User Details
                print("\n--- USER DETAILS ---")
                try:
                    user_id = int(input("Enter User ID: ").strip())
                    user = manager.get_user(user_id)
                    
                    if user:
                        print(f"\n📋 User Details:")
                        print(f"  ID: {user['id']}")
                        print(f"  Name: {user['name']}")
                        print(f"  Email: {user['email']}")
                        print(f"  Status: {'Active' if user.get('active', True) else 'Inactive'}")
                    else:
                        print(f"❌ User with ID {user_id} not found.")
                except ValueError:
                    print("❌ Please enter a valid number.")
            
            elif choice == "4":
                # Delete User
                print("\n--- DELETE USER ---")
                try:
                    user_id = int(input("Enter User ID to delete: ").strip())
                    
                    confirm = input(f"Are you sure you want to delete user {user_id}? (y/n): ").lower()
                    if confirm == 'y':
                        if manager.delete_user(user_id):
                            print(f"✅ User {user_id} marked as inactive.")
                        else:
                            print(f"❌ Failed to delete user {user_id}.")
                except ValueError:
                    print("❌ Please enter a valid number.")
            
            elif choice == "5":
                # Exit
                print("\n👋 Thank you for using User Management System!")
                print("Logs have been saved for review.")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-5.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Program interrupted. Exiting...")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            logger.error(f"Unexpected error in main loop: {e}")


if __name__ == "__main__":
    main()
