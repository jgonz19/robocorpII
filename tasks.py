from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    # To slow down the speed of the robot
    # browser.configure(
    #     slowmo = 500
    # )
    
    #Open the Website
    open_robot_order_website()
    orders = get_orders()
    for item in orders:
        fill_the_form(item)
    
    

def open_robot_order_website():
    """Open the website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """get the files from URL and save locally"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    return orders

def close_annoying_modal():
     """click on the button ok to close the popup"""
     close_popUp = browser.page()
     close_popUp.click("button:text('ok')")

def fill_the_form(item):
    """ to fill and click the options in the form """
    close_annoying_modal()
    page = browser.page()
    page.select_option("#head",item["Head"])
    page.check(f"#id-body-" + item["Body"])
    page.fill(".form-control", item["Legs"])
    page.fill("#address", item["Address"])
    page.click("#preview")
    page.click("#order")

    while not page.query_selector("#order-another"):
        page.click("#order")

    store_receipt_as_pdf(item["Order number"])

    page.click("#order-another")

    archive_receipts()

def store_receipt_as_pdf(order_number):
    """Store the reciept as pdf and we call the function embed_screenshot_to_receipt() to add pics to pdf"""
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_file = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(receipt, pdf_file)

    screenshot = f"output/receipts/{order_number}.png"
    page.screenshot(path=screenshot)

    embed_screenshot_to_receipt(screenshot, pdf_file)


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Add files to the PDF"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    """Library to get save the """
    archive = Archive()
    #origen and destino, incluye para establecer los archivos que queremos guardar
    archive.archive_folder_with_zip("output/receipts","output/receipts.zip",include="*.pdf")