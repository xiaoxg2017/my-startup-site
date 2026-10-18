# Saddle Point Productions website

Static website for saddlepointpro.com, hosted on Cloudflare Pages from this GitHub repo.

## Folder layout

- `public/` is the website. Cloudflare serves only this folder.
- `public/data/events.json` is the trade show calendar data. Edit this file to add or update shows.
- `tools/build.py` regenerates the HTML pages from shared templates.
- `docs/STRATEGY.md` has the site audit, keyword map, and open items.

## Deploy (one-time setup)

1. **Upload to GitHub.** In the repo on github.com, choose Add file → Upload files. Drag in `public`, `tools`, `docs`, and `README.md`, then commit to `main`.
2. **Point Cloudflare at the new folder.** In Cloudflare, go to Workers & Pages → your project → Settings → Build. Set the build command to empty and the build output directory to `public`. Save, then trigger a new deployment, or push any commit.
3. **Check the live site.** Open these and confirm they load:
   - `https://saddlepointpro.com/`
   - `https://saddlepointpro.com/las-vegas-trade-show-calendar/`
   - `https://saddlepointpro.com/generic.html`, which should redirect to the LED page
4. **Remove the old template.** Once the new site is live, delete the old `html5up-massively` folder from the repo. It's no longer served, but it contains the old placeholder pages.

## Let search engines in

- **Check bot blocking.** In Cloudflare → Security → Bots, and in AI Crawl Control / managed robots.txt if it's on, make sure normal search crawlers like Googlebot and Bingbot aren't blocked. Then open `https://saddlepointpro.com/robots.txt`. It should match `public/robots.txt`, which allows everything and lists the sitemap.
- **Pick one domain version.** Use either `www` or the bare domain and redirect the other. The site's canonical tags use `https://saddlepointpro.com`.
- **Set up Google Search Console.** Verify the domain, submit `https://saddlepointpro.com/sitemap.xml`, and use URL Inspection on the home and calendar pages.

## Make the quote form deliver to your inbox

Right now, pressing "Send request" opens the visitor's email app with the request filled in, addressed to xiao@saddlepointpro.com. That works, but some visitors won't finish sending.

To receive submissions directly:

1. Create a free form at a service such as Formspree or Web3Forms. Use xiao@saddlepointpro.com as the destination.
2. Copy the endpoint URL it gives you.
3. In `tools/build.py`, find `data-endpoint=""` and paste the URL between the quotes. Then run `python3 tools/build.py`. Or edit `public/request-a-quote/index.html` directly.

## Update the trade show calendar

1. Open `public/data/events.json` and copy an existing event block.
2. Fill in every field:
   - `startDate` / `endDate` use the `YYYY-MM-DD` format. Leave both empty (`""`) if the organizer hasn't announced dates.
   - `status` is `confirmed` if you checked the organizer's own site, `reported` if the dates only come from other listings, or `unannounced` if there are no dates yet.
   - `sourceUrl` is the page where you found the dates. Set `lastVerified` to the date you checked.
3. Visitors see the change right away. To also update the pre-rendered list that search engines read, run `python3 tools/build.py` and commit `public/`.

Past shows are hidden automatically after their end date (Las Vegas time). You don't need to delete them.

Recheck "reported" shows monthly and switch them to "confirmed" once you've seen the dates on the organizer's site.

## Change the photos

The site uses free stock photos from Unsplash (free for commercial use under the [Unsplash License](https://unsplash.com/license)). They're all listed in one place: the `PHOTOS` list near the top of `tools/build.py`. Each photo has a name, such as `led-wall` or `truss-lights`, and the pages pick photos by name.

To swap in your own job photo:

1. Save it in `public/assets/img/photos/`, for example `led-wall.jpg`. A landscape photo about 1600 px wide and under 400 KB works well.
2. In `PHOTOS`, change that photo's `"src"` to `"/assets/img/photos/led-wall.jpg"`. Update `"alt"` to describe your photo, and set `"credit"` and `"credit_url"` to `""`.
3. Run `python3 tools/build.py` and commit.

## Edit page text

Page copy lives in `tools/build.py`. Each page is one function, such as `build_home` and `build_services`. Edit the text, run `python3 tools/build.py` (Python 3.8+, no installs), and commit. Small one-off edits can also be made directly in the HTML files under `public/`. Just remember a rebuild will overwrite them.
