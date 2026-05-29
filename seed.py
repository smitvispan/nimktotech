import pymysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SOCKET

db = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    unix_socket=DB_SOCKET,
    cursorclass=pymysql.cursors.DictCursor,
)
cursor = db.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE businesses")
cursor.execute("TRUNCATE TABLE categories")
cursor.execute("TRUNCATE TABLE locations")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

locations = [
    'Rajkot', 'Ahmedabad', 'Surat', 'Vadodara', 'Jamnagar', 'Bhavnagar',
    'Junagadh', 'Morbi', 'Gondal', 'Jetpur'
]
for name in locations:
    cursor.execute("INSERT INTO locations (name) VALUES (%s)", (name,))

categories = [
    'Hardware', 'Restaurant', 'Electronics', 'Furniture', 'Pharmacy',
    'Clothing', 'Grocery', 'Automobile', 'Building Material', 'Sanitaryware'
]
for name in categories:
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))

db.commit()

# (location_id, category_id)
# locations: Rajkot=1, Ahmedabad=2, Surat=3, Vadodara=4, Jamnagar=5, Bhavnagar=6, Junagadh=7, Morbi=8, Gondal=9, Jetpur=10
# categories: Hardware=1, Restaurant=2, Electronics=3, Furniture=4, Pharmacy=5, Clothing=6, Grocery=7, Automobile=8, Building Material=9, Sanitaryware=10

businesses = [
    # ========== RAJKOT - HARDWARE (many) ==========
    ('Raj Hardware Store', 1, 1, 'https://rajhardware.com', 'info@rajhardware.com', 'Rajesh Patel', 'https://linkedin.com/in/rajeshpatel'),
    ('Shyam Hardware & Tools', 1, 1, 'https://shyamhardware.in', 'shyam@shyamhardware.in', 'Shyam Shah', 'https://linkedin.com/in/shyamshah'),
    ('Gujarat Hardware Center', 1, 1, 'https://gujarathardware.co.in', 'contact@gujarathardware.co.in', 'Amit Mehta', 'https://linkedin.com/in/amitmehta'),
    ('Chetan Hardware Stores', 1, 1, 'https://chetanhardware.com', 'chetan@chetanhardware.com', 'Chetan Kotecha', 'https://linkedin.com/in/chetankotecha'),
    ('Hardware Khazana', 1, 1, 'https://hardwarekhazana.in', 'info@hardwarekhazana.in', 'Sankar Bhai', 'https://linkedin.com/in/sankarbhai'),
    ('Hardware Junction', 1, 1, 'https://hardwarejunction.in', 'info@hardwarejunction.in', 'Jignesh Mehta', 'https://linkedin.com/in/jigneshmehta'),
    ('The Hardware Ocean', 1, 1, 'https://thehardwareocean.com', 'info@thehardwareocean.com', 'Manoj Solanki', 'https://linkedin.com/in/manojsolanki'),
    ('Devshree The Hardware Gallery', 1, 1, 'https://devshreehardware.com', 'devshree@devshreehardware.com', 'Devshree Patel', 'https://linkedin.com/in/devshreepatel'),
    ('Khedut Hardware & Paints', 1, 1, 'https://kheduthardware.com', 'info@kheduthardware.com', 'Karshan Bhai', 'https://linkedin.com/in/karshanbhai'),
    ('Hardware Angel', 1, 1, 'https://hardwareangel.in', 'info@hardwareangel.in', 'Angel Shah', 'https://linkedin.com/in/angelshah'),
    ('Shri Ramkrishna Hardware', 1, 1, 'https://ramkrishnahardware.com', 'ramkrishna@hardware.com', 'Ramkrishna Dave', 'https://linkedin.com/in/ramkrishnadave'),
    ('Shree Hardware', 1, 1, 'https://shreehardware.in', 'info@shreehardware.in', 'Shree Patel', 'https://linkedin.com/in/shreepatel'),
    ('Shree Ram Hardware', 1, 1, 'https://shreeramhardware.in', 'contact@shreeramhardware.in', 'Ram Bhai', 'https://linkedin.com/in/rambhai'),
    ('Abdulali Bodalbhai & Sons', 1, 1, 'https://abdulalibodalbhai.com', 'info@abdulalibodalbhai.com', 'Abdulali Bodalbhai', 'https://linkedin.com/in/abdulalibodalbhai'),
    ('Romex India Hardware Products', 1, 1, 'https://romexindia.in', 'info@romexindia.in', 'Romex Shah', 'https://linkedin.com/in/romexshah'),
    ('Poojasales Hardware', 1, 1, 'https://poojasales.com', 'info@poojasales.com', 'Pooja Mehta', 'https://linkedin.com/in/poojamehta'),
    ('Red Berry Hardware', 1, 1, 'https://redberryhardware.com', 'info@redberryhardware.com', 'Red Berry Patel', 'https://linkedin.com/in/redberrypatel'),
    ('Ketan Hardware And Sanitaries', 1, 1, 'https://ketanhardware.com', 'info@ketanhardware.com', 'Ketan Shah', 'https://linkedin.com/in/ketanshah'),
    ('Shree Chandarana Sales Corporation', 1, 1, 'https://chandaranasales.com', 'sales@chandaranasales.com', 'Chandarana Shah', 'https://linkedin.com/in/chandaranashah'),
    ('Radhika Enterprise', 1, 1, 'https://radhikaenterprise.in', 'info@radhikaenterprise.in', 'Radhika Patel', 'https://linkedin.com/in/radhikapatel'),
    ('Shree Mahakali Hardware', 1, 1, 'https://mahakalihardware.com', 'info@mahakalihardware.com', 'Mahakali Dave', 'https://linkedin.com/in/mahakalidave'),
    ('Rita Electric Stores', 1, 1, 'https://ritaelectric.in', 'info@ritaelectric.in', 'Shantilal V. Kotecha', 'https://linkedin.com/in/shantilalkotecha'),
    ('Dikay Hardware Industries Pvt Ltd', 1, 1, 'https://dikayhardware.com', 'info@dikayhardware.com', 'Denis Kotecha', 'https://linkedin.com/in/deniskotecha'),
    ('Zolon Architectural Hardware', 1, 1, 'https://zolonhardware.com', 'info@zolonhardware.com', 'Zolon Shah', 'https://linkedin.com/in/zolonshah'),
    ('Shailesh Tools', 1, 1, 'https://shaileshtools.in', 'info@shaileshtools.in', 'Shailesh Patel', 'https://linkedin.com/in/shaileshpatel'),
    ('Usha Manufactures', 1, 1, 'https://ushamanufactures.com', 'info@ushamanufactures.com', 'Usha Patel', 'https://linkedin.com/in/ushapatel'),
    ('Khodiyar Metal', 1, 1, 'https://khodiyarmetal.com', 'info@khodiyarmetal.com', 'Khodiyar Bhai', 'https://linkedin.com/in/khodiyarbhai'),
    ('Dev Enterprise', 1, 1, 'https://deventerprise.in', 'info@deventerprise.in', 'Dev Bhai', 'https://linkedin.com/in/devbhai'),
    ('Omega Enterprise', 1, 1, 'https://omegaenterprise.in', 'info@omegaenterprise.in', 'Omega Shah', 'https://linkedin.com/in/omegashah'),
    ('Benchmark Hardware', 1, 1, 'https://benchmarkhardware.in', 'info@benchmarkhardware.in', 'Benchmark Patel', 'https://linkedin.com/in/benchmarkpatel'),
    ('Niki Industries', 1, 1, 'https://nikiindustries.com', 'info@nikiindustries.com', 'Niki Shah', 'https://linkedin.com/in/nikishah'),
    ('Palak Industries', 1, 1, 'https://palakindustries.com', 'info@palakindustries.com', 'Palak Mehta', 'https://linkedin.com/in/palakmehta'),
    ('SP Metal', 1, 1, 'https://spmetal.in', 'silica.hardware@yahoo.com', 'Shailesh B Patel', 'https://linkedin.com/in/shaileshbpatel'),
    ('Steelera Industries', 1, 1, 'https://steeleraindia.com', 'info@steeleraindia.com', 'Steelera Patel', 'https://linkedin.com/in/steelerapatel'),
    ('R V M Furniture', 1, 4, 'https://rvmfurniture.com', 'info@rvmfurniture.com', 'RVM Bhai', 'https://linkedin.com/in/rvmbhai'),
    ('Doyours Interior', 1, 4, 'https://doyoursinterior.com', 'info@doyoursinterior.com', 'Doyours Patel', 'https://linkedin.com/in/doyourspatel'),
    # More Rajkot Hardware from RHMA directory
    ('Santkrupa Industries', 1, 1, 'https://santkrupa.in', 'info@santkrupa.in', 'Santkrupa Patel', 'https://linkedin.com/in/santkrupapatel'),
    ('Siddheshwar Metal', 1, 1, 'https://siddheshwar.in', 'info@siddheshwar.in', 'Siddheshwar Shah', 'https://linkedin.com/in/siddheshwarshah'),
    ('Darshan Metal Craft', 1, 1, 'https://darshanmetal.in', 'info@darshanmetal.in', 'Darshan Mehta', 'https://linkedin.com/in/darshanmehta'),
    ('Shreenath Products', 1, 1, 'https://shreenath.in', 'info@shreenath.in', 'Shreenath Dave', 'https://linkedin.com/in/shreenathdave'),
    ('Mahadev Metal', 1, 1, 'https://mahadevmetal.in', 'info@mahadevmetal.in', 'Mahadev Patel', 'https://linkedin.com/in/mahadevpatel'),
    ('Ghanshaym Metal Products', 1, 1, 'https://ghanshaym.in', 'info@ghanshaym.in', 'Ghanshaym Bhai', 'https://linkedin.com/in/ghanshaymbhai'),
    ('Vittoria Designs Pvt Ltd', 1, 1, 'https://vittoriadesigns.com', 'info@vittoriadesigns.com', 'Vittoria Shah', 'https://linkedin.com/in/vittoriashah'),
    ('Shreeji Industries', 1, 1, 'https://shreejiindustries.in', 'info@shreejiindustries.in', 'Shreeji Patel', 'https://linkedin.com/in/shreejipatel'),
    ('Classic Sales', 1, 1, 'https://classicsales.in', 'info@classicsales.in', 'Classic Mehta', 'https://linkedin.com/in/classicmehta'),
    ('PR Hardware', 1, 1, 'https://prhardware.in', 'info@prhardware.in', 'PR Patel', 'https://linkedin.com/in/prpatel'),
    ('MK Sales Corporation', 1, 1, 'https://mksales.in', 'info@mksales.in', 'MK Shah', 'https://linkedin.com/in/mkshah'),
    ('Accurate Door Device', 1, 1, 'https://accuratedoor.in', 'info@accuratedoor.in', 'Accurate Patel', 'https://linkedin.com/in/accuratepatel'),
    ('Patidar Metal Industries', 1, 1, 'https://patidarmetal.in', 'info@patidarmetal.in', 'Patidar Bhai', 'https://linkedin.com/in/patidarbhai'),
    ('Parth Industries', 1, 1, 'https://parthindustries.in', 'info@parthindustries.in', 'Parth Mehta', 'https://linkedin.com/in/parthmehta'),
    ('Somnath Technocast', 1, 1, 'https://somnath.in', 'info@somnath.in', 'Somnath Dave', 'https://linkedin.com/in/somnathdave'),
    ('Darshna Hardware Product', 1, 1, 'https://darshnahardware.in', 'info@darshnahardware.in', 'Darshna Shah', 'https://linkedin.com/in/darshnashah'),
    ('Radhe Industries', 1, 1, 'https://radheindustries.in', 'info@radheindustries.in', 'Radhe Patel', 'https://linkedin.com/in/radhepatel'),
    ('Tab Interior Product Pvt Ltd', 1, 1, 'https://tabinterior.in', 'info@tabinterior.in', 'Tab Shah', 'https://linkedin.com/in/tabshah'),
    ('Mundra Marketing System', 1, 1, 'https://mundramarketing.in', 'info@mundramarketing.in', 'Mundra Patel', 'https://linkedin.com/in/mundrapatel'),
    ('Arth Industries', 1, 1, 'https://arthindustries.in', 'info@arthindustries.in', 'Arth Mehta', 'https://linkedin.com/in/arthmehta'),
    ('Krupali Industries', 1, 1, 'https://krupali.in', 'info@krupali.in', 'Krupali Shah', 'https://linkedin.com/in/krupalishah'),
    ('Nilo Industries', 1, 1, 'https://niloindustries.in', 'info@niloindustries.in', 'Nilo Patel', 'https://linkedin.com/in/nilopatels'),
    ('Hardwell Industries', 1, 1, 'https://hardwellindustries.in', 'info@hardwellindustries.in', 'Hardwell Bhai', 'https://linkedin.com/in/hardwellbhai'),
    ('Maruti Enterprise', 1, 1, 'https://marutienterprise.in', 'info@marutienterprise.in', 'Maruti Shah', 'https://linkedin.com/in/marutishah'),
    ('Uno Enterprise', 1, 1, 'https://unoenterprise.in', 'info@unoenterprise.in', 'Uno Patel', 'https://linkedin.com/in/unopatels'),
    ('Creative Industries', 1, 1, 'https://creativeindustries.in', 'info@creativeindustries.in', 'Creative Mehta', 'https://linkedin.com/in/creativemehta'),
    ('R K Enterprise', 1, 1, 'https://rkenterprise.in', 'info@rkenterprise.in', 'RK Shah', 'https://linkedin.com/in/rkshah'),
    ('Sisko International', 1, 1, 'https://sisko.in', 'info@sisko.in', 'Sisko Patel', 'https://linkedin.com/in/siskopatels'),
    ('Fortune Hardware', 1, 1, 'https://fortunehardware.in', 'info@fortunehardware.in', 'Fortune Shah', 'https://linkedin.com/in/fortuneshah'),
    ('Black & White Hardware Pvt Ltd', 1, 1, 'https://bwhardware.in', 'info@bwhardware.in', 'BW Patel', 'https://linkedin.com/in/bwpatel'),
    ('Kiara Slides India Pvt Ltd', 1, 1, 'https://kiaraslides.com', 'info@kiaraslides.com', 'Kiara Shah', 'https://linkedin.com/in/kiarashah'),
    ('Sanvi Enterprise', 1, 1, 'https://sanvienterprise.com', 'info@sanvienterprise.com', 'Sanvi Patel', 'https://linkedin.com/in/sanvipatel'),
    ('Shree Hari Hardware', 1, 1, 'https://shreeharihardware.in', 'info@shreeharihardware.in', 'Shree Hari Patel', 'https://linkedin.com/in/shreeharipatel'),
    ('Bajrang Hardware', 1, 1, 'https://bajranghardware.in', 'info@bajranghardware.in', 'Bajrang Bhai', 'https://linkedin.com/in/bajrangbhai'),
    ('Amar Hardware Products', 1, 1, 'https://amarhardware.in', 'info@amarhardware.in', 'Amar Shah', 'https://linkedin.com/in/amarshah'),
    ('Satyam Hardware Product', 1, 1, 'https://satyamhardware.in', 'info@satyamhardware.in', 'Satyam Patel', 'https://linkedin.com/in/satyampatel'),
    ('Shivam Metal', 1, 1, 'https://shivammetal.in', 'info@shivammetal.in', 'Shivam Shah', 'https://linkedin.com/in/shivamshah'),
    ('Golden White Industries', 1, 1, 'https://goldenwhite.in', 'info@goldenwhite.in', 'Golden Patel', 'https://linkedin.com/in/goldenpatel'),
    ('Bold Incorporation', 1, 1, 'https://boldincorporation.in', 'info@boldincorporation.in', 'Bold Shah', 'https://linkedin.com/in/boltshah'),
    ('Krishna Enterprise', 1, 1, 'https://krishnaenterprise.in', 'info@krishnaenterprise.in', 'Krishna Mehta', 'https://linkedin.com/in/krishnamehta'),
    ('Vidhi Enterprise & Hardware', 1, 1, 'https://vidhienterprise.in', 'info@vidhienterprise.in', 'Vidhi Shah', 'https://linkedin.com/in/vidhishah'),
    ('Shree Sainath Metal Industries', 1, 1, 'https://sainathmetal.in', 'info@sainathmetal.in', 'Sainath Patel', 'https://linkedin.com/in/sainathpatel'),
    ('Apex Technocast', 1, 1, 'https://apextechnocast.in', 'info@apextechnocast.in', 'Apex Shah', 'https://linkedin.com/in/apexshah'),
    ('Alfa Techno', 1, 1, 'https://alfatechno.in', 'info@alfatechno.in', 'Alfa Patel', 'https://linkedin.com/in/alfapatel'),
    ('Rajesh Engineering Works', 1, 1, 'https://rajeshengineering.in', 'info@rajeshengineering.in', 'Rajesh Bhai', 'https://linkedin.com/in/rajeshbhai'),
    ('Shakti Hardware', 1, 1, 'https://shaktihardware.in', 'info@shaktihardware.in', 'Shakti Shah', 'https://linkedin.com/in/shaktishah'),
    ('Bharat Hardware Product', 1, 1, 'https://bharathardware.in', 'info@bharathardware.in', 'Bharat Patel', 'https://linkedin.com/in/bharatpatel'),
    ('Maruti Hardware', 1, 1, 'https://marutihardware.in', 'info@marutihardware.in', 'Maruti Bhai', 'https://linkedin.com/in/marutibhai'),
    ('Balaji Hardware Products', 1, 1, 'https://balajihardware.in', 'info@balajihardware.in', 'Balaji Shah', 'https://linkedin.com/in/balajishah'),
    ('Shreeja Hardware', 1, 1, 'https://shreejahardware.in', 'info@shreejahardware.in', 'Shreeja Patel', 'https://linkedin.com/in/shreejapatel'),
    ('Agrawal Hardware', 1, 1, 'https://agrawalhardware.in', 'info@agrawalhardware.in', 'Agrawal Shah', 'https://linkedin.com/in/agrawalshah'),
    ('Alfa Hardware Industries', 1, 1, 'https://alfahardware.in', 'info@alfahardware.in', 'Alfa Bhai', 'https://linkedin.com/in/alfabhai'),
    ('Zenith Sales', 1, 1, 'https://zenithsales.in', 'info@zenithsales.in', 'Zenith Patel', 'https://linkedin.com/in/zenithpatel'),
    ('Radhika Industries', 1, 1, 'https://radhikaindustries.in', 'info@radhikaindustries.in', 'Radhika Shah', 'https://linkedin.com/in/radhikashah'),
    ('Uno Door Closer', 1, 1, 'https://unodoorcloser.com', 'info@unodoorcloser.com', 'Uno Patel', 'https://linkedin.com/in/unopatels'),
    ('Jay Vrundavan Industries', 1, 1, 'https://jayvrundavanindustries.com', 'info@jayvrundavan.com', 'Jay Vrundavan', 'https://linkedin.com/in/jayvrundavan'),
    ('Skevi Interior Products Pvt Ltd', 1, 1, 'https://skevi.in', 'info@skevi.in', 'Skevi Shah', 'https://linkedin.com/in/skevishah'),
    ('Dreamtech Hardware', 1, 1, 'https://dreamtechhardware.com', 'info@dreamtechhardware.com', 'Dreamtech Patel', 'https://linkedin.com/in/dreamtechpatel'),
    ('Octoriahardware', 1, 1, 'https://octoriahardware.com', 'info@octoriahardware.com', 'Octoria Shah', 'https://linkedin.com/in/octoriashah'),
    ('Galaxy Technocast', 1, 1, 'https://galaxytechnocast.in', 'info@galaxytechnocast.in', 'Galaxy Mehta', 'https://linkedin.com/in/galaxymehta'),
    ('Rudra Enterprise', 1, 1, 'https://rudraenterprise.in', 'info@rudraenterprise.in', 'Rudra Bhai', 'https://linkedin.com/in/rudrabhai'),
    ('Servo Tech Industries', 1, 1, 'https://servotech.in', 'info@servotech.in', 'Servo Patel', 'https://linkedin.com/in/servopatels'),

    # ========== RAJKOT - OTHER CATEGORIES ==========
    ('Gujarat Dhaba', 1, 2, 'https://gujaratdhaba.com', 'order@gujaratdhaba.com', 'Kishor Dave', 'https://linkedin.com/in/kishordave'),
    ('Rajkot Food Plaza', 1, 2, 'https://rajkotfoodplaza.com', 'info@rajkotfoodplaza.com', 'Mehul Joshi', 'https://linkedin.com/in/mehuljoshi'),
    ('Sai Electronics', 1, 3, 'https://saielectronics.in', 'support@saielectronics.in', 'Saurabh Desai', 'https://linkedin.com/in/saurabhdesai'),
    ('Digital World Rajkot', 1, 3, 'https://digitalworldrajkot.com', 'info@digitalworldrajkot.com', 'Nikhil Trivedi', 'https://linkedin.com/in/nikhiltrivedi'),

    # ========== OTHER CITIES - HARDWARE ==========
    ('Ahmedabad Hardware Mart', 2, 1, 'https://ahmedabadhardware.com', 'info@ahmedabadhardware.com', 'Dinesh Shah', 'https://linkedin.com/in/dineshshah'),
    ('Metro Hardware Store', 2, 1, 'https://metrohardware.com', 'contact@metrohardware.com', 'Prakash Patel', 'https://linkedin.com/in/prakashpatel'),
    ('Surat Hardware & Pipes', 3, 1, 'https://surathardware.com', 'info@surathardware.com', 'Mukesh Agarwal', 'https://linkedin.com/in/mukeshagarwal'),
    ('Baroda Furniture House', 4, 4, 'https://barodafurniture.com', 'sales@barodafurniture.com', 'Vijay Rao', 'https://linkedin.com/in/vijayrao'),
    ('Jamnagar Medical Store', 5, 5, 'https://jamnagarmedical.com', 'info@jamnagarmedical.com', 'Rakesh Joshi', 'https://linkedin.com/in/rakeshjoshi'),
    ('Bhavnagar Fashion Hub', 6, 6, 'https://bhavnagarfashion.com', 'info@bhavnagarfashion.com', 'Hitesh Gohil', 'https://linkedin.com/in/hiteshgohil'),
]

for b in businesses:
    cursor.execute(
        "INSERT INTO businesses (name, location_id, category_id, website, email, owner_name, owner_linkedin) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        b,
    )

db.commit()
cursor.close()
db.close()
# Count Rajkot hardware
rajkot_hardware = [b for b in businesses if b[1] == 1 and b[2] == 1]
print(f"✅ Seed data inserted: {len(businesses)} businesses total")
print(f"✅ Rajkot Hardware: {len(rajkot_hardware)} businesses")
print(f"✅ Locations: {len(locations)}, Categories: {len(categories)}")
