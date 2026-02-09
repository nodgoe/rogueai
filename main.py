import curses
import random
import time

class RogueGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.dungeon_width = 20
        self.dungeon_height = 15
        self.rooms = []
        self.corridors = []
        self.player_x = 0
        self.player_y = 0
        self.game_over = False
        self.score = 0
        self.current_room = 0
        
        # Player stats
        self.player_health = 20
        self.player_max_health = 20
        self.player_attack = random.randint(1, 5)
        
        # Game elements
        self.enemies = []
        self.items = []
        
        # Initialize the dungeon
        self.generate_dungeon()
        self.place_player()
        self.generate_elements()
        
    def generate_dungeon(self):
        """Generate a dungeon with multiple rooms and corridors"""
        self.rooms = []
        self.corridors = []
        
        # Create rooms - try to create 4-6 rooms
        num_rooms = random.randint(4, 6)
        
        for i in range(num_rooms):
            # Try to place a room
            placed = False
            max_attempts = 100
            
            for attempt in range(max_attempts):
                # Fixed room size of 7x7
                width = 7
                height = 7
                
                # Random position
                x = random.randint(0, self.dungeon_width - width - 1)
                y = random.randint(0, self.dungeon_height - height - 1)
                
                # Check if room overlaps with existing rooms
                overlap = False
                for room in self.rooms:
                    if (x < room['x'] + room['width'] and 
                        x + width > room['x'] and 
                        y < room['y'] + room['height'] and 
                        y + height > room['y']):
                        overlap = True
                        break
                
                if not overlap:
                    # Place the room
                    self.rooms.append({
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'id': i
                    })
                    placed = True
                    break
            
            # If we couldn't place a room, try with minimum size room
            if not placed:
                width = 7
                height = 7
                x = random.randint(0, self.dungeon_width - width - 1)
                y = random.randint(0, self.dungeon_height - height - 1)
                
                # Check if room overlaps with existing rooms
                overlap = False
                for room in self.rooms:
                    if (x < room['x'] + room['width'] and 
                        x + width > room['x'] and 
                        y < room['y'] + room['height'] and 
                        y + height > room['y']):
                        overlap = True
                        break
                
                if not overlap:
                    self.rooms.append({
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'id': i
                    })
        
        # Connect rooms with corridors
        self.create_corridors()
        
    def create_corridors(self):
        """Create corridors connecting rooms with 1-4 hallways"""
        self.corridors = []
        
        if len(self.rooms) < 2:
            return
            
        # Connect each room to the next one in sequence
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            
            # Get center points of rooms
            center1_x = room1['x'] + room1['width'] // 2
            center1_y = room1['y'] + room1['height'] // 2
            center2_x = room2['x'] + room2['width'] // 2
            center2_y = room2['y'] + room2['height'] // 2
            
            # Create horizontal corridor (1 character wide)
            if center1_x < center2_x:
                self.corridors.append({
                    'x': center1_x,
                    'y': center1_y,
                    'width': center2_x - center1_x,
                    'height': 1,
                    'type': 'horizontal'
                })
            else:
                self.corridors.append({
                    'x': center2_x,
                    'y': center1_y,
                    'width': center1_x - center2_x,
                    'height': 1,
                    'type': 'horizontal'
                })
            
            # Create vertical corridor (1 character wide)
            if center1_y < center2_y:
                self.corridors.append({
                    'x': center2_x,
                    'y': center1_y,
                    'width': 1,
                    'height': center2_y - center1_y,
                    'type': 'vertical'
                })
            else:
                self.corridors.append({
                    'x': center2_x,
                    'y': center2_y,
                    'width': 1,
                    'height': center1_y - center2_y,
                    'type': 'vertical'
                })
    
    def place_player(self):
        """Place player in the first room"""
        if self.rooms:
            first_room = self.rooms[0]
            self.player_x = first_room['x'] + first_room['width'] // 2
            self.player_y = first_room['y'] + first_room['height'] // 2
            self.current_room = 0
    
    def generate_elements(self):
        """Generate enemies and items in the dungeon"""
        self.enemies = []
        self.items = []
        
        # Place enemies in each room
        for room in self.rooms:
            num_enemies = random.randint(1, 3)  # 1-3 enemies per room
            for _ in range(num_enemies):
                x = random.randint(room['x'] + 1, room['x'] + room['width'] - 2)
                y = random.randint(room['y'] + 1, room['y'] + room['height'] - 2)
                # Create enemy with attack 1-2 and health 5
                self.enemies.append({
                    'x': x, 
                    'y': y, 
                    'symbol': 'E', 
                    'health': 5,
                    'attack': random.randint(1, 2)
                })
        
        # Place items in each room
        for room in self.rooms:
            num_items = random.randint(2, 5)  # 2-5 items per room
            for _ in range(num_items):
                x = random.randint(room['x'] + 1, room['x'] + room['width'] - 2)
                y = random.randint(room['y'] + 1, room['y'] + room['height'] - 2)
                self.items.append({'x': x, 'y': y, 'symbol': '$'})
    
    def draw_dungeon(self):
        """Draw the entire dungeon with rooms and corridors"""
        self.stdscr.clear()
        
        # Draw each room
        for room in self.rooms:
            # Draw room walls
            for y in range(room['y'], room['y'] + room['height']):
                for x in range(room['x'], room['x'] + room['width']):
                    # Draw walls
                    if (x == room['x'] or x == room['x'] + room['width'] - 1 or 
                        y == room['y'] or y == room['y'] + room['height'] - 1):
                        self.stdscr.addch(y + 1, x + 1, '#', curses.color_pair(1))
                    else:
                        self.stdscr.addch(y + 1, x + 1, '.')
        
        # Draw corridors
        for corridor in self.corridors:
            for y in range(corridor['y'], corridor['y'] + corridor['height']):
                for x in range(corridor['x'], corridor['x'] + corridor['width']):
                    self.stdscr.addch(y + 1, x + 1, '.')
        
        # Draw enemies
        for enemy in self.enemies:
            if self.is_in_room(enemy['x'], enemy['y']):
                self.stdscr.addch(enemy['y'] + 1, enemy['x'] + 1, enemy['symbol'], curses.color_pair(2))
        
        # Draw items
        for item in self.items:
            if self.is_in_room(item['x'], item['y']):
                self.stdscr.addch(item['y'] + 1, item['x'] + 1, item['symbol'], curses.color_pair(3))
        
        # Draw player
        self.stdscr.addch(self.player_y + 1, self.player_x + 1, '@', curses.color_pair(4))
        
        # Draw UI
        self.stdscr.addstr(0, 0, f"Score: {self.score}  |  Room: {self.current_room + 1}  |  Use arrow keys to move. Press 'q' to quit.")
        self.stdscr.addstr(1, 0, f"Health: {self.player_health}/{self.player_max_health}  |  Attack: {self.player_attack}  |  Enemies: {len(self.enemies)}  |  Items: {len(self.items)}")
        
        self.stdscr.refresh()
    
    def is_in_room(self, x, y):
        """Check if coordinates are in any room"""
        for room in self.rooms:
            if (room['x'] <= x < room['x'] + room['width'] and 
                room['y'] <= y < room['y'] + room['height']):
                return True
        return False
    
    def move_player(self, dx, dy):
        """Move the player by dx, dy"""
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Check if move is within dungeon bounds
        if (0 <= new_x < self.dungeon_width and 
            0 <= new_y < self.dungeon_height):
            
            # Check if new position is not a wall
            is_valid = False
            
            # Check if in a room
            for room in self.rooms:
                if (room['x'] <= new_x < room['x'] + room['width'] and 
                    room['y'] <= new_y < room['y'] + room['height']):
                    is_valid = True
                    break
            
            # Check if in a corridor
            if not is_valid:
                for corridor in self.corridors:
                    if (corridor['x'] <= new_x < corridor['x'] + corridor['width'] and 
                        corridor['y'] <= new_y < corridor['y'] + corridor['height']):
                        is_valid = True
                        break
            
            if is_valid:
                self.player_x = new_x
                self.player_y = new_y
                
                # Check for item collection
                self.check_item_collection()
                
                # Check for enemy collision
                self.check_enemy_collision()
                
                # Update current room
                self.update_current_room()
                
                # Move enemies after player movement
                self.move_enemies()
                
                return True
        return False
    
    def move_enemies(self):
        """Move enemies toward the player"""
        for enemy in self.enemies:
            # Calculate direction to player
            dx = self.player_x - enemy['x']
            dy = self.player_y - enemy['y']
            
            # Normalize direction
            if dx != 0:
                dx = dx // abs(dx)
            if dy != 0:
                dy = dy // abs(dy)
            
            # Try to move in the direction of the player
            new_x = enemy['x'] + dx
            new_y = enemy['y'] + dy
            
            # Check if new position is valid (not a wall)
            is_valid = False
            
            # Check if in a room
            for room in self.rooms:
                if (room['x'] <= new_x < room['x'] + room['width'] and 
                    room['y'] <= new_y < room['y'] + room['height']):
                    is_valid = True
                    break
            
            # Check if in a corridor
            if not is_valid:
                for corridor in self.corridors:
                    if (corridor['x'] <= new_x < corridor['x'] + corridor['width'] and 
                        corridor['y'] <= new_y < corridor['y'] + corridor['height']):
                        is_valid = True
                        break
            
            # Move enemy if valid position
            if is_valid:
                enemy['x'] = new_x
                enemy['y'] = new_y
                
                # Check if enemy caught player
                if enemy['x'] == self.player_x and enemy['y'] == self.player_y:
                    # Enemy attacks player
                    self.player_health -= enemy['attack']
                    if self.player_health <= 0:
                        self.player_health = 0
                        self.game_over = True
                    # Remove enemy
                    self.enemies.remove(enemy)
    
    def update_current_room(self):
        """Update which room the player is currently in"""
        for i, room in enumerate(self.rooms):
            if (room['x'] <= self.player_x < room['x'] + room['width'] and 
                room['y'] <= self.player_y < room['y'] + room['height']):
                self.current_room = i
                return
    
    def check_item_collection(self):
        """Check if player collected an item"""
        for i, item in enumerate(self.items):
            if item['x'] == self.player_x and item['y'] == self.player_y:
                self.items.pop(i)
                self.score += 10
                # Increase player health when collecting items
                self.player_health = min(self.player_max_health, self.player_health + 5)
                return
    
    def check_enemy_collision(self):
        """Check if player collided with an enemy"""
        for i, enemy in enumerate(self.enemies):
            if enemy['x'] == self.player_x and enemy['y'] == self.player_y:
                # Player attacks enemy
                enemy['health'] -= self.player_attack
                if enemy['health'] <= 0:
                    # Enemy defeated
                    self.enemies.pop(i)
                    self.score += 20
                else:
                    # Enemy attacks back
                    self.player_health -= enemy['attack']
                    if self.player_health <= 0:
                        self.player_health = 0
                        self.game_over = True
                return
    
    def run(self):
        """Main game loop"""
        # Setup colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Walls
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Enemies
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Items
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Player
        
        # Hide cursor
        curses.curs_set(0)
        
        while not self.game_over:
            self.draw_dungeon()
            
            # Get user input
            key = self.stdscr.getch()
            
            # Handle input
            if key == ord('q'):
                self.game_over = True
            elif key == curses.KEY_UP:
                self.move_player(0, -1)
            elif key == curses.KEY_DOWN:
                self.move_player(0, 1)
            elif key == curses.KEY_LEFT:
                self.move_player(-1, 0)
            elif key == curses.KEY_RIGHT:
                self.move_player(1, 0)
            
            # Small delay to control game speed
            time.sleep(0.1)
        
        # Game over screen
        self.stdscr.clear()
        self.stdscr.addstr(self.height // 2, self.width // 2 - 5, "GAME OVER")
        self.stdscr.addstr(self.height // 2 + 1, self.width // 2 - 8, f"Final Score: {self.score}")
        self.stdscr.addstr(self.height // 2 + 3, self.width // 2 - 10, "Press any key to exit")
        self.stdscr.refresh()
        self.stdscr.getch()

def main(stdscr):
    game = RogueGame(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)