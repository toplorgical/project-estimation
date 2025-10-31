from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from pricing.models import Supplier, PriceData
from materials.models import Material, MaterialCategory
from machinery.models import Machinery, MachineryCategory
import random


class Command(BaseCommand):
    help = 'Populate database with sample materials, machinery, and pricing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Only populate if no sample data exists (idempotent guard)',
        )

    def handle(self, *args, **options):
        # Idempotent guard
        if options.get('if-empty'):
            # If we already have any suppliers AND any price data, consider populated
            if Supplier.objects.exists() and PriceData.objects.exists():
                self.stdout.write(self.style.SUCCESS('✓ Sample data already present, skipping population'))
                return

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            PriceData.objects.all().delete()
            Material.objects.all().delete()
            MaterialCategory.objects.all().delete()
            Machinery.objects.all().delete()
            MachineryCategory.objects.all().delete()
            Supplier.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

        # Create suppliers
        self.stdout.write('Creating suppliers...')
        suppliers = self.create_suppliers()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(suppliers)} suppliers'))

        # Create material categories and materials
        self.stdout.write('Creating materials...')
        materials = self.create_materials()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(materials)} materials'))

        # Create machinery categories and machinery
        self.stdout.write('Creating machinery...')
        machinery = self.create_machinery()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(machinery)} machinery'))

        # Create pricing data
        self.stdout.write('Creating pricing data...')
        price_count = self.create_pricing_data(suppliers, materials, machinery)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {price_count} price records'))

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data population complete!'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(suppliers)} suppliers'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(materials)} materials'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(machinery)} machinery'))
        self.stdout.write(self.style.SUCCESS(f'   - {price_count} price records'))

    def create_suppliers(self):
        suppliers_data = [
            ('Travis Perkins', 'https://www.travisperkins.co.uk', 'sales@travisperkins.co.uk'),
            ('Wickes', 'https://www.wickes.co.uk', 'info@wickes.co.uk'),
            ('Screwfix', 'https://www.screwfix.com', 'customer.services@screwfix.com'),
            ('Toolstation', 'https://www.toolstation.com', 'customer.services@toolstation.com'),
            ('B&Q', 'https://www.diy.com', 'customer.services@diy.com'),
            ('Homebase', 'https://www.homebase.co.uk', 'customer.services@homebase.co.uk'),
            ('Buildbase', 'https://www.buildbase.co.uk', 'info@buildbase.co.uk'),
            ('Jewson', 'https://www.jewson.co.uk', 'enquiries@jewson.co.uk'),
        ]

        suppliers = []
        for name, website, email in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'website': website,
                    'contact_email': email,
                    'is_active': True,
                    'locations': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow']
                }
            )
            suppliers.append(supplier)

        return suppliers

    def create_materials(self):
        # Create categories
        categories_data = [
            ('Cement & Aggregates', 'Cement, sand, gravel, and aggregates'),
            ('Bricks & Blocks', 'Building bricks, blocks, and masonry'),
            ('Timber & Sheet Materials', 'Wood, plywood, MDF, and sheet materials'),
            ('Plumbing Supplies', 'Pipes, fittings, and plumbing fixtures'),
            ('Electrical Supplies', 'Cables, switches, and electrical fittings'),
            ('Roofing Materials', 'Tiles, felt, and roofing supplies'),
            ('Insulation', 'Thermal and acoustic insulation'),
            ('Paint & Decorating', 'Paint, wallpaper, and decorating supplies'),
            ('Tools & Hardware', 'Hand tools, power tools, and hardware'),
            ('Flooring', 'Tiles, carpet, laminate, and flooring'),
        ]

        categories = {}
        for name, desc in categories_data:
            category, created = MaterialCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            categories[name] = category

        # Create materials
        materials_data = [
            # Cement & Aggregates
            ('Portland Cement', 'Cement & Aggregates', 'Generic', 'bag', 'CEM001', 25, 350),
            ('Sharp Sand', 'Cement & Aggregates', 'Generic', 'tonne', 'SND001', 1000, 25),
            ('Building Sand', 'Cement & Aggregates', 'Generic', 'tonne', 'SND002', 1000, 28),
            ('Gravel 10mm', 'Cement & Aggregates', 'Generic', 'tonne', 'GRV001', 1000, 30),
            ('Ballast', 'Cement & Aggregates', 'Generic', 'tonne', 'BAL001', 1000, 32),
            
            # Bricks & Blocks
            ('Red Facing Brick', 'Bricks & Blocks', 'Hanson', 'piece', 'BRK001', 2.5, 0.45),
            ('Concrete Block 100mm', 'Bricks & Blocks', 'Tarmac', 'piece', 'BLK001', 3.5, 1.20),
            ('Aerated Block 100mm', 'Bricks & Blocks', 'Celcon', 'piece', 'BLK002', 1.8, 2.50),
            ('Engineering Brick Class B', 'Bricks & Blocks', 'Ibstock', 'piece', 'BRK002', 3.0, 0.55),
            
            # Timber & Sheet Materials
            ('Plywood 18mm', 'Timber & Sheet Materials', 'Generic', 'sheet', 'PLY001', 15, 28),
            ('OSB Board 11mm', 'Timber & Sheet Materials', 'Generic', 'sheet', 'OSB001', 12, 12),
            ('MDF Board 18mm', 'Timber & Sheet Materials', 'Generic', 'sheet', 'MDF001', 14, 18),
            ('CLS Timber 47x100mm', 'Timber & Sheet Materials', 'Generic', 'm', 'TIM001', 1.5, 3.20),
            ('Sawn Timber 50x150mm', 'Timber & Sheet Materials', 'Generic', 'm', 'TIM002', 2.5, 4.50),
            
            # Plumbing
            ('Copper Pipe 15mm', 'Plumbing Supplies', 'Pegler', 'm', 'COP001', 0.5, 4.50),
            ('Copper Pipe 22mm', 'Plumbing Supplies', 'Pegler', 'm', 'COP002', 0.8, 6.80),
            ('PVC Waste Pipe 40mm', 'Plumbing Supplies', 'Floplast', 'm', 'PVC001', 0.3, 2.20),
            ('Push-Fit Elbow 15mm', 'Plumbing Supplies', 'John Guest', 'piece', 'FIT001', 0.02, 1.50),
            
            # Electrical
            ('2.5mm Twin & Earth Cable', 'Electrical Supplies', 'Prysmian', 'm', 'CAB001', 0.08, 1.20),
            ('1.5mm Twin & Earth Cable', 'Electrical Supplies', 'Prysmian', 'm', 'CAB002', 0.05, 0.85),
            ('Double Socket White', 'Electrical Supplies', 'MK Electric', 'piece', 'SOC001', 0.15, 3.50),
            ('Light Switch 1 Gang', 'Electrical Supplies', 'MK Electric', 'piece', 'SW001', 0.08, 2.20),
        ]

        materials = []
        for name, cat_name, brand, unit, sku, weight, price in materials_data:
            material, created = Material.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': categories[cat_name],
                    'unit': unit,
                    'brand': brand,
                    'weight': Decimal(str(weight)),
                    'is_active': True,
                    'description': f'High quality {name.lower()} for construction projects'
                }
            )
            materials.append((material, price))

        return materials

    def create_machinery(self):
        # Create categories
        categories_data = [
            ('Excavators', 'Diggers and excavation equipment'),
            ('Access Equipment', 'Scaffolding, ladders, and access towers'),
            ('Power Tools', 'Electric and pneumatic power tools'),
            ('Lifting Equipment', 'Cranes, hoists, and lifting gear'),
            ('Concrete Equipment', 'Mixers, vibrators, and concrete tools'),
            ('Compaction Equipment', 'Rollers, rammers, and compactors'),
        ]

        categories = {}
        for name, desc in categories_data:
            category, created = MachineryCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            categories[name] = category

        # Create machinery
        machinery_data = [
            ('Mini Excavator 1.5T', 'Excavators', 'Kubota', 'KX018-4', 'diesel', 15, 'EXC001', 150, 600),
            ('Mini Excavator 3T', 'Excavators', 'JCB', '8030', 'diesel', 25, 'EXC002', 200, 800),
            ('Scaffold Tower 4m', 'Access Equipment', 'Youngman', 'Boss', 'manual', 80, 'ACC001', 40, 150),
            ('Mobile Scaffold 6m', 'Access Equipment', 'Youngman', 'BoSS', 'manual', 120, 'ACC002', 60, 220),
            ('Concrete Mixer 110v', 'Concrete Equipment', 'Belle', 'Minimix 150', 'electric', 0.6, 'MIX001', 35, 140),
            ('Concrete Mixer Diesel', 'Concrete Equipment', 'Belle', 'Maxi 140', 'diesel', 5, 'MIX002', 50, 200),
            ('Breaker 110v', 'Power Tools', 'Makita', 'HM1307CB', 'electric', 1.5, 'BRK001', 30, 120),
            ('Angle Grinder 230mm', 'Power Tools', 'DeWalt', 'DWE490', 'electric', 0.5, 'GRN001', 15, 60),
            ('Plate Compactor', 'Compaction Equipment', 'Wacker', 'WP1550AW', 'petrol', 4.5, 'COM001', 40, 160),
            ('Roller Compactor', 'Compaction Equipment', 'Belle', 'PCLX 320', 'diesel', 8, 'COM002', 50, 200),
        ]

        machinery = []
        for name, cat_name, brand, model, fuel, power, sku, daily, weekly in machinery_data:
            machine, created = Machinery.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': categories[cat_name],
                    'brand': brand,
                    'model': model,
                    'fuel_type': fuel,
                    'power': f'{power}kW' if fuel != 'manual' else 'Manual',
                    'is_active': True,
                    'description': f'Professional grade {name.lower()} for construction work'
                }
            )
            machinery.append((machine, daily, weekly))

        return machinery

    def create_pricing_data(self, suppliers, materials, machinery):
        count = 0
        locations = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow', 'Bristol', 'Newcastle']

        # Create pricing for materials
        for material, base_price in materials:
            for supplier in random.sample(suppliers, k=random.randint(3, 6)):
                for location in random.sample(locations, k=random.randint(2, 4)):
                    # Add some price variation (±15%)
                    price_variation = random.uniform(0.85, 1.15)
                    price = round(base_price * price_variation, 2)

                    PriceData.objects.create(
                        material=material,
                        supplier=supplier,
                        price=Decimal(str(price)),
                        unit=material.unit,
                        in_stock=random.choice([True, True, True, False]),  # 75% in stock
                        location=location,
                        is_active=True,
                        scraped_at=timezone.now()
                    )
                    count += 1

        # Create pricing for machinery
        for machine, daily_rate, weekly_rate in machinery:
            for supplier in random.sample(suppliers, k=random.randint(2, 4)):
                for location in random.sample(locations, k=random.randint(2, 3)):
                    # Add some price variation
                    daily_variation = random.uniform(0.9, 1.1)
                    weekly_variation = random.uniform(0.9, 1.1)

                    PriceData.objects.create(
                        machinery=machine,
                        supplier=supplier,
                        price=Decimal(str(round(daily_rate * 7 * daily_variation, 2))),  # Purchase price estimate
                        rental_price_daily=Decimal(str(round(daily_rate * daily_variation, 2))),
                        rental_price_weekly=Decimal(str(round(weekly_rate * weekly_variation, 2))),
                        unit='day',
                        in_stock=random.choice([True, True, False]),  # 66% available
                        location=location,
                        is_active=True,
                        scraped_at=timezone.now()
                    )
                    count += 1

        return count
