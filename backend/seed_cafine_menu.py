import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from canteens.models import Canteen
from accounts.models import CanteenAdminProfile
from menu.models import FoodCategory, FoodItem

User = get_user_model()

def seed_cafine():
    print("Seeding Cafine (Engineering Block Cafeteria) Menu...")

    # 1. Update or create Canteen 'Cafine'
    try:
        cafine = Canteen.objects.get(id=2)
        cafine.name = 'Cafine'
        cafine.description = 'Specialty cafe, artisan hot brews, burgers, subs, grilled toasts, pizzas and creamy shakes at Engineering Block, Medi-Caps University.'
        cafine.location = 'Engineering Block, Medi-Caps University Campus, AB Road, Indore'
        cafine.is_active = True
        cafine.save()
        print(f"[OK] Renamed canteen id=2 to '{cafine.name}'")
    except Canteen.DoesNotExist:
        cafine, _ = Canteen.objects.get_or_create(
            name='Cafine',
            defaults={
                'description': 'Specialty cafe, artisan hot brews, burgers, subs, grilled toasts, pizzas and creamy shakes at Engineering Block, Medi-Caps University.',
                'location': 'Engineering Block, Medi-Caps University Campus, AB Road, Indore',
                'is_active': True,
            }
        )
        print(f"[OK] Created canteen '{cafine.name}'")

    # 2. Ensure Admin accounts for Cafine
    admin_emails = ['cafine@medicaps.ac.in', 'engg.canteen@medicaps.ac.in']
    for email in admin_emails:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': 'Cafine Engineering Manager',
                'mobile': '9826099887',
                'role': 'canteen_admin',
                'is_staff': True,
            }
        )
        user.set_password('Cafine@123')
        user.role = 'canteen_admin'
        user.is_staff = True
        user.save()

        profile, _ = CanteenAdminProfile.objects.get_or_create(user=user, defaults={'canteen': cafine})
        profile.canteen = cafine
        profile.save()
        print(f"[OK] Set up Admin {email} / Cafine@123 for Cafine")

    # 3. Categories to create for Cafine
    categories_def = [
        ('Hot Beverages', 1, 'Freshly brewed chai, espresso, and warming teas'),
        ('Burgers', 2, 'Gourmet burgers grilled with signature sauces and fillings'),
        ('Subs', 3, 'Hearty 6-inch subs with fresh veggies and dressings'),
        ('Cold Beverages', 4, 'Iced teas, cold coffees, coolers and sodas'),
        ('Mojitos', 5, 'Refreshing fizzy fruit and mint mocktails'),
        ('Parathas', 6, 'Tawa and tandoori parathas served fresh'),
        ('Sandwiches', 7, 'Grilled and toasted sandwiches packed with cheese and fillings'),
        ('Pizzas', 8, 'Fresh-baked thin crust and pan pizzas with mozzarella'),
        ('Garlic Bread & Toast', 9, 'Crunchy garlic breads, cheesy toasts, and snacks'),
        ('Soups', 10, 'Hot comforting bowls of soup'),
        ('Pastas', 11, 'Creamy Italian pastas tossed in aromatic herbs'),
        ('Maggi & Noodles', 12, 'Campus favorite Maggi variants loaded with toppings'),
        ('Milkshakes', 13, 'Thick creamy milkshakes blended with chocolate and fruit'),
        ('Happiness & Bakery', 14, 'Brownies, samosas, bread butter and sweet treats'),
        ('Crispy Fries', 15, 'Golden crispy potato fries seasoned to perfection'),
    ]

    cat_map = {}
    for cat_name, order, desc in categories_def:
        cat, _ = FoodCategory.objects.get_or_create(
            canteen=cafine,
            name=cat_name,
            defaults={'order': order, 'description': desc, 'is_active': True}
        )
        cat_map[cat_name] = cat
    print(f"[OK] Configured {len(cat_map)} categories for Cafine.")

    # 4. Clear old items for cafine to avoid duplication
    FoodItem.objects.filter(canteen=cafine).delete()
    print("[OK] Reset previous items for Cafine.")

    # 5. Food items from user prompt
    items_data = [
        # Hot Beverages
        ('Tea (Regular)', 'Hot Beverages', 10, 'Classic Indian spiced cutting tea brewed fresh.', True),
        ('Tea (Special Big)', 'Hot Beverages', 15, 'Large cup of premium aromatic milk tea.', True),
        ('Coffee (Regular)', 'Hot Beverages', 25, 'Rich roasted hot milk coffee.', True),
        ('Coffee (Big)', 'Hot Beverages', 50, 'Large frothy aromatic coffee.', True),
        ('Hot Lemon Tea (Small)', 'Hot Beverages', 30, 'Invigorating black tea with fresh lemon zest.', True),
        ('Hot Lemon Tea (Big)', 'Hot Beverages', 50, 'Large hot lemon tea infused with citrus herbs.', True),
        ('Black Coffee (Small)', 'Hot Beverages', 30, 'Intense dark roast espresso shot coffee.', True),
        ('Black Coffee (Big)', 'Hot Beverages', 50, 'Double shot rich Americano black coffee.', True),

        # Burgers
        ('Classic Burger', 'Burgers', 55, 'Golden veggie patty, fresh tomato, crisp lettuce & mayo.', True),
        ('Peri Peri Burger', 'Burgers', 75, 'Spicy peri-peri seasoned patty with fiery chipotle sauce.', True),
        ('Cheese Burger', 'Burgers', 65, 'Melted cheddar slice over savory vegetable patty.', True),
        ('Tandoori Burger', 'Burgers', 75, 'Smoky tandoori paneer patty with mint mayo and onions.', True),

        # Subs
        ('Salad Sub', 'Subs', 95, 'Fresh bell peppers, cucumbers, lettuce, olives & vinaigrette.', True),
        ('Mexican Sub', 'Subs', 100, 'Zesty Mexican bean patty, jalapeños, salsa and cheese.', True),
        ('Paneer Sub', 'Subs', 115, 'Marinated spiced paneer cubes, crunchy veggies & mayo.', True),
        ('Schezwan Sub', 'Subs', 100, 'Spicy Schezwan tossed filling with garlic and peppers.', True),

        # Cold Beverages
        ('Lemon Ice Tea', 'Cold Beverages', 50, 'Chilled brewed iced tea with lemon and crushed mint.', True),
        ('Peach Ice Tea', 'Cold Beverages', 60, 'Sweet aromatic peach iced tea served super chilled.', True),
        ('Cold Coffee', 'Cold Beverages', 70, 'Classic creamy blended iced coffee.', True),
        ('Cold Chocolate', 'Cold Beverages', 70, 'Decadent rich dark cocoa iced drink.', True),
        ('Cold Coffee With Ice Cream', 'Cold Beverages', 80, 'Thick cold coffee crowned with a vanilla scoop.', True),
        ('Limewater', 'Cold Beverages', 30, 'Hydrating fresh lime water sweet or salted.', True),
        ('Lime Soda', 'Cold Beverages', 40, 'Sparkling soda with fresh lime juice and black salt.', True),
        ('Hazelnut Syrup (Add-on)', 'Cold Beverages', 15, 'Flavor shot of nutty Italian hazelnut syrup.', True),

        # Mojitos
        ('Mint Mojito', 'Mojitos', 70, 'Crushed fresh garden mint, lemon wedges, and soda.', True),
        ('Peach Mojito', 'Mojitos', 75, 'Juicy sweet peach infused fizzy cooler.', True),
        ('Green Apple Mojito', 'Mojitos', 75, 'Crisp tangy green apple cooler with bubbly soda.', True),

        # Parathas
        ('Aloo Paratha', 'Parathas', 70, 'Whole wheat flatbread stuffed with spiced mashed potatoes.', True),
        ('Paneer Paratha', 'Parathas', 80, 'Grated fresh cottage cheese stuffed paratha with butter.', True),
        ('Sev Paratha', 'Parathas', 65, 'Authentic Indore crispy sev and onion stuffed paratha.', True),

        # Sandwiches
        ('Masala Grill Sandwich', 'Sandwiches', 50, 'Spiced potato filling grilled golden in butter.', True),
        ('Cheese Chutney Sandwich', 'Sandwiches', 60, 'Spicy coriander-mint chutney with gooey melted cheese.', True),
        ('Cheese Corn Sandwich', 'Sandwiches', 65, 'Sweet golden corn kernels mixed with melted mozzarella.', True),
        ('Veg Cheese Sandwich', 'Sandwiches', 55, 'Sliced garden veggies and cheese grilled crisp.', True),
        ('Chilly Paneer Sandwich', 'Sandwiches', 65, 'Wok-tossed chilli paneer slices packed in bread.', True),
        ('Paneer Tikka Sandwich', 'Sandwiches', 70, 'Smoky paneer tikka chunks with capsicum and cheese.', True),

        # Pizzas
        ('Cheese Pizza', 'Pizzas', 99, 'Classic 7-inch crust loaded with 100% mozzarella cheese.', True),
        ('Cheese Corn Pizza', 'Pizzas', 99, 'Golden sweet corn sprinkled over rich tomato sauce & cheese.', True),
        ('Onion Paneer Pizza', 'Pizzas', 115, 'Crisp onions and fresh spiced paneer cubes on pizza sauce.', True),
        ('Makhni Paneer Pizza', 'Pizzas', 115, 'Creamy makhni gravy base topped with paneer & cheese.', True),

        # Garlic Bread & Toast
        ('Cheesy Garlic Bread', 'Garlic Bread & Toast', 85, 'Crisp French bread baked with garlic butter & cheese.', True),
        ('Pizza Toast', 'Garlic Bread & Toast', 60, 'Toasted bread topped with pizza sauce, veggies and cheese.', True),
        ('Cheese Chilly Toast', 'Garlic Bread & Toast', 50, 'Finely chopped green chillies and molten cheese toast.', True),
        ('Chilly Garlic Bread', 'Garlic Bread & Toast', 70, 'Spicy garlic butter rubbed bread with chilli flakes.', True),

        # Soups
        ('Tomato Soup', 'Soups', 30, 'Silky ripe tomato soup served with crispy croutons.', True),
        ('Corn Soup', 'Soups', 30, 'Sweet corn broth with diced veggies and white pepper.', True),
        ('Manchow Soup', 'Soups', 30, 'Spicy Indo-Chinese dark soup topped with crispy fried noodles.', True),

        # Pastas
        ('White Sauce Pasta', 'Pastas', 80, 'Penne pasta tossed in rich cheesy béchamel white sauce.', True),
        ('Red Sauce Pasta', 'Pastas', 80, 'Tangy herb tomato marinara pasta with bell peppers.', True),
        ('Mix Sauce Pasta', 'Pastas', 80, 'Pink sauce blend of creamy white and tangy arrabbiata sauces.', True),

        # Maggi & Noodles
        ('Classic Maggi', 'Maggi & Noodles', 50, 'Nostalgic 2-minute instant noodles cooked to perfection.', True),
        ('Masala Maggi', 'Maggi & Noodles', 60, 'Loaded with extra Indian spices, onions, and tomatoes.', True),
        ('Cheese Maggi', 'Maggi & Noodles', 70, 'Decadent creamy Maggi draped in gooey melted cheese.', True),
        ('Veggie Maggi', 'Maggi & Noodles', 70, 'Packed with carrots, peas, corn, and fresh capsicum.', True),
        ('Chilly Garlic Maggi', 'Maggi & Noodles', 60, 'Spiced up with crushed garlic and red chilli oil.', True),
        ('Butter Garlic Maggi', 'Maggi & Noodles', 65, 'Rich butter sautéed garlic infused aromatic Maggi.', True),

        # Milkshakes
        ('KitKat Milkshake', 'Milkshakes', 70, 'Crunchy KitKat bars blended with chocolate ice cream.', True),
        ('Oreo Milkshake', 'Milkshakes', 70, 'Thick vanilla shake infused with Oreo cookie crumbs.', True),
        ('Butterscotch Milkshake', 'Milkshakes', 70, 'Creamy butterscotch crunch and caramel syrup.', True),
        ('Mango Milkshake', 'Milkshakes', 70, 'Rich Alphonso mango pulp blended in thick cold milk.', True),
        ('Strawberry Milkshake', 'Milkshakes', 70, 'Sweet pink strawberry shake crowned with strawberry drizzle.', True),
        ('Nutella Milkshake', 'Milkshakes', 80, 'Hazelnut cocoa Nutella generously blended with ice cream.', True),
        ('Brownie Milkshake', 'Milkshakes', 80, 'Fudgy chocolate brownie pieces blended into a thick shake.', True),

        # Happiness & Bakery
        ('Brownie With Ice Cream', 'Happiness & Bakery', 80, 'Warm chocolate walnut brownie served with vanilla ice cream.', True),
        ('Bread Butter (2 Slice)', 'Happiness & Bakery', 30, 'Soft fresh bread slices smeared with creamy salted Amul butter.', True),
        ('Bread Jam (2 Slice)', 'Happiness & Bakery', 30, 'Sweet mixed fruit Kissan jam on soft bread slices.', True),
        ('Baked Samosa (Plain)', 'Happiness & Bakery', 25, 'Flaky golden baked pastry stuffed with spiced potatoes.', True),
        ('Baked Samosa With Sauces', 'Happiness & Bakery', 35, 'Crushed baked samosa drizzled with sweet tamarind and mint chutneys.', True),

        # Crispy Fries
        ('Salted / Masala Fries', 'Crispy Fries', 60, 'Deep fried potato batons dusted with chaat masala or sea salt.', True),
        ('Peri Peri / Cheese Fries', 'Crispy Fries', 80, 'Crispy French fries tossed in fiery peri-peri and melted cheese.', True),
    ]

    created_count = 0
    for name, cat_name, price, desc, is_veg in items_data:
        cat = cat_map[cat_name]
        FoodItem.objects.create(
            canteen=cafine,
            category=cat,
            name=name,
            price=Decimal(str(price)),
            description=desc,
            is_veg=is_veg,
            is_available=True,
            preparation_time=10,
        )
        created_count += 1

    print(f"[SUCCESS] Successfully seeded {created_count} food items for '{cafine.name}'!")

if __name__ == '__main__':
    seed_cafine()
