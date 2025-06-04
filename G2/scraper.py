# scraper.py
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time

OUTPUT_FILE = "G2_SaaS_Insights.xlsx"
DELAY = 2  # polite delay between actions (in seconds)

results = []

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.bigideasdb.com/saas-analysis")
        await page.wait_for_timeout(DELAY * 1000)

        # Expand all categories
        expand_buttons = await page.query_selector_all(".accordion-button")
        for button in expand_buttons:
            try:
                await button.click()
                await page.wait_for_timeout(DELAY * 500)
            except:
                continue

        # Get all "Details" links
        detail_links = await page.query_selector_all("a:has-text('Details')")

        for btn in detail_links:
            link = await btn.get_attribute('href')
            if not link:
                continue
            full_url = f"https://www.bigideasdb.com{link}"
            subcategory_name = await btn.inner_text()

            subpage = await context.new_page()
            await subpage.goto(full_url)
            await subpage.wait_for_timeout(DELAY * 1000)

            company_cards = await subpage.query_selector_all("div.card-body")
            for card in company_cards:
                try:
                    company_name = await card.query_selector("h5")
                    company = await company_name.inner_text()
                    description = (await card.inner_text()).split("\n")[0]

                    view_btn = await card.query_selector("text=View Insights")
                    await view_btn.click()
                    await subpage.wait_for_timeout(DELAY * 1000)

                    insights = {}
                    for tab in ["Summary", "Analysis", "Opportunities"]:
                        try:
                            await subpage.click(f"text={tab}")
                            await subpage.wait_for_timeout(DELAY * 500)
                            sections = await subpage.query_selector_all(".css-1y6sixo")
                            texts = [await s.inner_text() for s in sections]
                            insights[tab] = texts
                        except:
                            insights[tab] = []

                    results.append({
                        "Category": subcategory_name,
                        "Company": company,
                        "Description": description,
                        "Overall Sentiment": insights["Summary"][0] if len(insights["Summary"]) > 0 else "",
                        "Pain Points": insights["Summary"][1] if len(insights["Summary"]) > 1 else "",
                        "Proposed Solution": insights["Summary"][2] if len(insights["Summary"]) > 2 else "",
                        "User Impact": insights["Analysis"][0] if len(insights["Analysis"]) > 0 else "",
                        "Risk Factors": insights["Analysis"][1] if len(insights["Analysis"]) > 1 else "",
                        "Business Model": insights["Analysis"][2] if len(insights["Analysis"]) > 2 else "",
                        "Market Opportunity": insights["Opportunities"][0] if len(insights["Opportunities"]) > 0 else "",
                        "Competitive Advantage": insights["Opportunities"][1] if len(insights["Opportunities"]) > 1 else "",
                        "Business Model (2)": insights["Opportunities"][2] if len(insights["Opportunities"]) > 2 else ""
                    })

                    await subpage.click("button:has-text('×')")  # Close modal
                    await subpage.wait_for_timeout(DELAY * 500)

                except Exception as e:
                    print(f"Error with company: {e}")
                    continue

            await subpage.close()
            await page.bring_to_front()
            await page.wait_for_timeout(DELAY * 500)

        await browser.close()

    df = pd.DataFrame(results)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Scraping complete. Saved to {OUTPUT_FILE}")


# To run this script manually
if __name__ == "__main__":
    asyncio.run(scrape())
