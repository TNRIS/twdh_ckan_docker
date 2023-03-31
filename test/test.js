import puppeteer from "puppeteer";

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.goto("http://0.0.0.0:5000");

  await page.setViewport({ width: 1080, height: 1024 });

  await page.type("#table_filter", "Data Dan");

  await page.click("#searchBtn");

  await page.waitForSelector(".search-results");

  await page.screenshot({
    path: "screenshots/searchResults.png",
    fullPage: true,
  });
  console.log("test complete");

  await browser.close();
})();
