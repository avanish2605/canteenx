import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, CanteenAdminProfile
from canteens.models import Canteen
from menu.models import FoodCategory, FoodItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds initial data for Medi-Caps University CanteenX application'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting initial data seeding for CanteenX...'))

        # 1. Super Admin
        super_admin_email = 'admin@medicaps.ac.in'
        if not User.objects.filter(email=super_admin_email).exists():
            super_admin = User.objects.create_superuser(
                email=super_admin_email,
                full_name='Medi-Caps Super Admin',
                password='Admin@123',
                mobile='9876543210'
            )
            self.stdout.write(self.style.SUCCESS(f'Created Super Admin: {super_admin_email} / Admin@123'))
        else:
            self.stdout.write('Super Admin already exists.')

        # 2. Main Canteen
        canteen, created = Canteen.objects.get_or_create(
            name='Medi-Caps Central Canteen',
            defaults={
                'description': 'The primary student and faculty food court serving fresh, hygienic, and affordable meals across all university departments.',
                'location': 'Ground Floor, Block B, Medi-Caps University Campus, AB Road, Indore, MP 453331',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Canteen: {canteen.name}'))

        # Secondary Canteen for multi-canteen demonstration
        canteen2, _ = Canteen.objects.get_or_create(
            name='Engineering Block Cafeteria',
            defaults={
                'description': 'Quick bites, premium coffee, fresh beverages, and breakfast snacks for engineering students and faculty.',
                'location': 'Near Mechanical Engineering Workshop, Medi-Caps University',
                'is_active': True,
            }
        )

        # 3. Canteen Admin
        canteen_admin_email = 'canteen@medicaps.ac.in'
        if not User.objects.filter(email=canteen_admin_email).exists():
            admin_user = User.objects.create_user(
                email=canteen_admin_email,
                full_name='Indore Canteen Manager',
                password='Canteen@123',
                mobile='9826012345',
                role='canteen_admin',
                is_staff=True
            )
            CanteenAdminProfile.objects.create(user=admin_user, canteen=canteen)
            self.stdout.write(self.style.SUCCESS(f'Created Canteen Admin: {canteen_admin_email} / Canteen@123'))
        else:
            self.stdout.write('Canteen Admin already exists.')

        # 4. Sample Student
        student_email = 'student@medicaps.ac.in'
        if not User.objects.filter(email=student_email).exists():
            student_user = User.objects.create_user(
                email=student_email,
                full_name='Atharv Sharma',
                password='Student@123',
                mobile='9893011223',
                role='student',
                is_active=True,
                is_email_verified=True,
            )
            StudentProfile.objects.create(user=student_user, enrollment_number='EN2024CS001')
            self.stdout.write(self.style.SUCCESS(f'Created Demo Student: {student_email} / Student@123'))
        else:
            self.stdout.write('Demo Student already exists.')

        # Ensure all existing seeded accounts are verified and active
        User.objects.filter(email__in=[
            'admin@medicaps.ac.in',
            'canteen@medicaps.ac.in',
            'cafine@medicaps.ac.in',
            'student@medicaps.ac.in'
        ]).update(is_email_verified=True, is_active=True)

        # 5. Food Categories
        categories_data = [
            {'name': 'Indori Breakfast', 'order': 1, 'description': 'Authentic morning specialties from Indore'},
            {'name': 'Lunch & Thali', 'order': 2, 'description': 'Wholesome North Indian and campus meal combos'},
            {'name': 'Fast Food & Snacks', 'order': 3, 'description': 'Burgers, sandwiches, noodles and evening quick bites'},
            {'name': 'Beverages & Shakes', 'order': 4, 'description': 'Chai, cold coffee, juices and refreshing coolers'},
            {'name': 'Desserts & Sweets', 'order': 5, 'description': 'Delicious traditional sweets and bakery treats'},
        ]

        cat_objs = {}
        for cat_info in categories_data:
            cat, _ = FoodCategory.objects.get_or_create(
                canteen=canteen,
                name=cat_info['name'],
                defaults={'order': cat_info['order'], 'description': cat_info['description'], 'is_active': True}
            )
            cat_objs[cat.name] = cat

        # 6. Food Items
        items_data = [
            # Breakfast
            {
                'category': 'Indori Breakfast',
                'name': 'Indori Sev Usal Poha',
                'description': 'Famous Indore style soft spiced flattened rice topped with crunchy Ratlami sev, onions, coriander and jeeravan.',
                'price': Decimal('35.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 5,
                'stock_quantity': 150,
            },
            {
                'category': 'Indori Breakfast',
                'name': 'Crispy Samosa with Chutney (2 Pcs)',
                'description': 'Hot crispy pastry stuffed with spiced potato and green peas, served with sweet tamarind and spicy mint chutneys.',
                'price': Decimal('30.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 5,
                'stock_quantity': 80,
            },
            {
                'category': 'Indori Breakfast',
                'name': 'South Indian Masala Dosa',
                'description': 'Thin golden crepe stuffed with spiced potato mash, served with coconut chutney and hot vegetable sambar.',
                'price': Decimal('75.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 12,
                'stock_quantity': 60,
            },
            {
                'category': 'Indori Breakfast',
                'name': 'Steamed Idli Sambhar (2 Pcs)',
                'description': 'Fluffy steamed rice and lentil cakes served with piping hot authentic sambar and fresh coconut dip.',
                'price': Decimal('50.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 6,
                'stock_quantity': 50,
            },
            {
                'category': 'Indori Breakfast',
                'name': 'Stuffed Aloo Paratha with Curd & Pickle',
                'description': 'Tawa grilled whole wheat flatbread loaded with spiced potato filling, served with fresh curd and mixed pickle.',
                'price': Decimal('60.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 10,
                'stock_quantity': 45,
            },

            # Lunch & Thali
            {
                'category': 'Lunch & Thali',
                'name': 'Medi-Caps Special Royal Thali',
                'description': 'Complete balanced meal with Shahi Paneer, Dal Makhani, 4 Butter Phulkas, Jeera Rice, Cucumber Raita, Papad, Salad & Gulab Jamun.',
                'price': Decimal('130.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 15,
                'stock_quantity': 100,
            },
            {
                'category': 'Lunch & Thali',
                'name': 'Executive Student Mini Thali',
                'description': 'Everyday campus special: Dal Tadka, Seasonal Mix Veg Curry, 4 Tawa Rotis, Plain Rice, and Fresh Green Salad.',
                'price': Decimal('80.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 10,
                'stock_quantity': 120,
            },
            {
                'category': 'Lunch & Thali',
                'name': 'Paneer Butter Masala with 3 Butter Naan',
                'description': 'Rich cottage cheese cubes simmered in velvety tomato cashew gravy, served with fluffy buttered naan.',
                'price': Decimal('145.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 15,
                'stock_quantity': 40,
            },
            {
                'category': 'Lunch & Thali',
                'name': 'Punjabi Chole Bhature (2 Large Bhature)',
                'description': 'Spicy chickpea curry cooked with aromatic spices, paired with two balloon puffed bhaturas, pickled onions, and green chilies.',
                'price': Decimal('90.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 12,
                'stock_quantity': 75,
            },
            {
                'category': 'Lunch & Thali',
                'name': 'Yellow Dal Fry with Jeera Rice Bowl',
                'description': 'Homestyle yellow toor lentil tempered with cumin, garlic and ghee, served over fragrant basmati jeera rice.',
                'price': Decimal('85.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 10,
                'stock_quantity': 60,
            },

            # Fast Food & Snacks
            {
                'category': 'Fast Food & Snacks',
                'name': 'Grilled Jumbo Cheese Sandwich',
                'description': 'Triple layer grilled sandwich with capsicum, tomatoes, sweet corn, melted mozzarella, and oregano seasoning.',
                'price': Decimal('70.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 8,
                'stock_quantity': 70,
            },
            {
                'category': 'Fast Food & Snacks',
                'name': 'Crispy Veg Patty Burger with Fries',
                'description': 'Crisp spiced veggie patty with fresh lettuce, sliced tomatoes, creamy chipotle mayo, served with salted potato fries.',
                'price': Decimal('85.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 10,
                'stock_quantity': 50,
            },
            {
                'category': 'Fast Food & Snacks',
                'name': 'Veg Hakka Noodles',
                'description': 'Wok tossed noodles loaded with crunchy cabbage, bell peppers, carrots, spring onions, and oriental sauces.',
                'price': Decimal('80.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 10,
                'stock_quantity': 60,
            },
            {
                'category': 'Fast Food & Snacks',
                'name': 'Veg Manchurian Dry (8 Pcs)',
                'description': 'Crispy vegetable florets tossed in zesty ginger, garlic, soy, and dark chili glaze topped with spring onions.',
                'price': Decimal('90.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 12,
                'stock_quantity': 45,
            },

            # Beverages & Shakes
            {
                'category': 'Beverages & Shakes',
                'name': 'Indori Kadak Masala Chai',
                'description': 'Traditional brewed milk tea infused with crushed ginger, green cardamom, cloves, and Indian spices.',
                'price': Decimal('15.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 3,
                'stock_quantity': 300,
            },
            {
                'category': 'Beverages & Shakes',
                'name': 'Thick Cold Coffee with Chocolate Ice Cream',
                'description': 'Chilled creamy blended coffee topped with a rich scoop of chocolate ice cream and Hershey drizzle.',
                'price': Decimal('60.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 5,
                'stock_quantity': 80,
            },
            {
                'category': 'Beverages & Shakes',
                'name': 'Sweet Lassi (Indori Kulhad)',
                'description': 'Traditional churned yogurt cooler served thick with a crown of clotted malai and chopped pistachios.',
                'price': Decimal('45.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 4,
                'stock_quantity': 50,
            },
            {
                'category': 'Beverages & Shakes',
                'name': 'Fresh Mint Lemonade Soda',
                'description': 'Fizzy refreshing soda with freshly squeezed Indore lemons, crushed mint leaves, rock salt, and cumin.',
                'price': Decimal('35.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 3,
                'stock_quantity': 100,
            },

            # Desserts
            {
                'category': 'Desserts & Sweets',
                'name': 'Hot Gulab Jamun in Saffron Syrup (2 Pcs)',
                'description': 'Golden fried mawa dumplings soaked in cardamom and saffron flavored sugar syrup. Served warm.',
                'price': Decimal('40.00'),
                'is_veg': True,
                'is_featured': True,
                'preparation_time': 3,
                'stock_quantity': 60,
            },
            {
                'category': 'Desserts & Sweets',
                'name': 'Warm Chocolate Walnut Brownie',
                'description': 'Fudgy chocolate brownie loaded with toasted walnuts and drizzled with warm dark chocolate ganache.',
                'price': Decimal('75.00'),
                'is_veg': True,
                'is_featured': False,
                'preparation_time': 4,
                'stock_quantity': 35,
            },
        ]

        created_count = 0
        for item_info in items_data:
            cat = cat_objs.get(item_info['category'])
            item, was_created = FoodItem.objects.get_or_create(
                canteen=canteen,
                name=item_info['name'],
                defaults={
                    'category': cat,
                    'description': item_info['description'],
                    'price': item_info['price'],
                    'is_veg': item_info['is_veg'],
                    'is_featured': item_info['is_featured'],
                    'preparation_time': item_info['preparation_time'],
                    'stock_quantity': item_info['stock_quantity'],
                    'is_available': True,
                }
            )
            if was_created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} food items successfully!'))
        self.stdout.write(self.style.SUCCESS('Initial data seeding completed for CanteenX!'))
