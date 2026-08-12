# Meta campaign implementation package

## Decision summary

Campaign goal: acquire qualified US private clients for Doychin Karshovski's performance and longevity advisory.

Recommended funnel:

`Meta ad -> doychin.com/private -> five-question fit check -> private scheduling page -> discovery conversation -> paid engagement`

The ad sells the conversation. The conversation determines fit and sells the relationship. Do not send cold traffic to the homepage, a checkout page, or the fully allocated Making Sense program.

## Guardrails

- Do not launch, schedule, publish, or spend money without Doych's explicit final approval.
- Use a website preview and complete the verification checklist before production.
- Keep all claims educational and general. Do not promise prevention, diagnosis, reversal, lifespan extension, or a medical outcome.
- Do not write copy that assumes or states a viewer's health condition, age-related decline, diagnosis, wealth, or other sensitive personal attribute.
- Do not send fit-check answers, medical details, free text, or scheduling notes to Meta.
- The landing-page fit check does not collect or store answers. Google requests contact details only after a visitor chooses to schedule.

## Campaign structure

| Setting | Recommendation |
| --- | --- |
| Buying type | Auction |
| Objective | Leads |
| Conversion location | Website |
| Destination | `https://www.doychin.com/private` |
| Initial optimization event | `Lead`, fired only on the outbound scheduling click |
| Market | United States |
| Age | 40 to 65 |
| Gender | All |
| Placements | Advantage+ placements |
| Test budget | $50 per day total, acceptable range $40 to $60 |
| Test duration | 21 days or until each ad set has enough signal for a responsible comparison |
| Budget method | Ad-set budgets for the first controlled test |
| Recommended split | $25 per day per ad set |
| Ads | Three creatives duplicated across both ad sets, six ads total |
| Attribution | Start with Meta's account default, record it in the launch log, and do not change it mid-test |

At $50 per day for 21 days, the planned ceiling is $1,050. Treat this as a test ceiling, not a commitment to spend. Doych must approve the final daily budget and launch.

## Two audience tests

### Audience 1: Broad high-performer prospecting

- United States
- Age 40 to 65
- All genders
- No narrow health or wellness interests
- Advantage+ placements
- Exclude existing paying clients and recent booked calls when clean suppression lists are available and lawful to use
- Let restrained creative and landing-page language do most of the qualification

Reason: Meta's delivery system generally needs room to learn. Narrow interest stacks can produce false precision and reduce scale.

### Audience 2: High-value similarity

Preferred setup:

- United States
- Age 40 to 65
- 1 to 3 percent lookalike built from a clean list of past high-value private clients
- Use only records that can lawfully and appropriately be used for advertising
- Exclude the source list and current clients

Fallback if there is no adequate first-party seed:

- Use a separate broad ad set with Advantage+ audience suggestions based on entrepreneurship, executive education, leadership, and performance
- Treat suggestions as signals, not hard restrictions
- Do not use health conditions, genetic traits, diagnoses, or inferred medical interests

Do not mix a small warm retargeting pool into the prospecting comparison. If there is enough traffic later, run retargeting as a separate campaign with its own budget and reporting.

## Creative concept 1: The stance

Format: restrained portrait of Doychin, 4:5 primary, adapted to 1:1 and 9:16.

On-image copy:

`DON'T WAIT UNTIL SOMETHING BREAKS.`

Primary text:

Most people start taking their health seriously when something goes wrong.

My clients prefer to start earlier.

They are founders, executives, professionals, and high performers who have spent years building careers, businesses, and families.

Eventually a different question matters: can your body and mind keep up with the life you have built?

I have spent more than 35 years working at the intersection of human performance, behavior, and longevity.

I do not sell motivation, quick fixes, or another collection of biohacks. We look at where you are, decide what matters, and build a system that fits real life.

I work privately with a limited number of clients. If you want to stay ahead, request a private conversation.

Headline: `Don't wait until something breaks.`

Description: `Private performance and longevity advisory.`

Meta CTA: `Learn More`

## Creative concept 2: The life you built

Format: 15 to 20 second direct-to-camera video. Clean background, natural light, no clinical props. Burn in captions because video often starts without sound.

Script:

You have spent years building your career, your business, and your life.

Here is the question most successful people ask too late: can your body and mind keep up with what you have built?

I help people look earlier, make sense of what matters, and build a system that fits real life.

Do not wait until something breaks.

Primary text:

Success creates options. It also creates demands.

Private advisory with Doychin Karshovski brings health data, performance, behavior, and real-life constraints into one clear conversation.

No miracle protocols. No generic plan. Clarity first, then action.

Headline: `Build capacity for the life ahead.`

Description: `A private conversation about what matters now.`

Meta CTA: `Learn More`

## Creative concept 3: The contrarian

Format: typography-led static image or restrained three-frame motion graphic using the existing ink, bone, and ember palette.

Frames:

1. `I DON'T SELL MOTIVATION.`
2. `I DON'T SELL BIOHACKS.`
3. `I HELP PEOPLE STAY AHEAD.`

Primary text:

More information is rarely the answer.

The useful questions are simpler: what matters now, what can wait, and what is only noise?

Doychin Karshovski works privately with a limited number of founders, executives, professionals, and other high performers who want clarity, structure, and honest guidance before the decisions become urgent.

Headline: `Clarity before optimization.`

Description: `Private advisory. Limited capacity.`

Meta CTA: `Learn More`

## Landing-page CTA

Use one action throughout the page:

`Request a private conversation`

Every instance moves the visitor to the same five-question fit check. The final instance opens the existing Google scheduling page.

## Qualification questions

The landing page asks only non-medical questions and does not submit or store the answers:

1. Which best describes your current work?
2. What would make this conversation useful now?
3. When would you want to begin, if the fit is right?
4. Which working style sounds most like you?
5. Private work may begin at $600, with deeper engagements from $2,400. Is that a range you are prepared to consider?

Recommended scheduling questions, configured inside Google only if needed:

1. What would make this conversation useful for you?
2. Why does this matter now?
3. What have you already tried?
4. Are you considering a Foundations Session, a deeper engagement, or are you not yet sure?

Keep scheduling answers out of Meta Pixel, Conversions API, URLs, and analytics. Do not request diagnoses, symptoms, genetic data, or raw health records in the advertising funnel.

## Tracking plan

### Browser events already hooked on `/private`

| Funnel action | Data-layer event | Meta event when consented | Use |
| --- | --- | --- | --- |
| Page load | `private_funnel` with `page_view` | Custom `PrivateFunnel` | Landing-page volume |
| First answer accepted | `private_funnel` with `qualification_started` | Custom `PrivateFunnel` | Fit-check start rate |
| Fifth answer accepted | `private_funnel` with `qualification_completed` | Custom `PrivateFunnel` | Completion rate |
| Scheduling link click | `private_funnel` with `schedule_click` | Standard `Lead` | Initial optimization event |

The page also emits a browser `private-funnel` custom event. The hooks contain only event names and the fixed page path. They do not contain answers, role, timing, budget response, health information, email, name, URL query values, or free text.

Meta calls are disabled by default. They run only when both the Meta base code exists and `window.setPrivateMarketingConsent(true)` has been called by an approved consent layer.

### Required before launch

1. Confirm the Meta dataset and Pixel ID in Events Manager.
2. Confirm the site has an appropriate consent mechanism before adding the Meta base code.
3. Connect the consent mechanism to `window.setPrivateMarketingConsent(true)` only after valid marketing consent when required.
4. Use Meta Test Events to verify `Lead` fires once on the final scheduling click, not on page view or fit-check completion.
5. Confirm no question answer or health-related data appears in event parameters, URLs, browser storage, or network requests.
6. Verify domain ownership and configure web events if the account requires it.
7. Add campaign UTMs to every ad URL.
8. Record booked calls, qualified calls, and paid clients in a private lead log. Where lawful and properly configured, send only appropriate downstream status events through Conversions API with deduplication.

### URL template

`https://www.doychin.com/private?utm_source=meta&utm_medium=paid_social&utm_campaign=pc_us_stay_ahead_test01&utm_content={{ad.name}}&utm_term={{adset.name}}`

Do not place names, emails, health terms, answers, or other personal data in UTM parameters.

### Decision metrics

Primary business metrics:

- Cost per booked private conversation
- Qualified-call rate
- Cost per qualified call
- Paid-client conversion rate
- Customer acquisition cost
- First-engagement revenue and expected client value

Diagnostic metrics:

- Landing-page view to fit-check start rate
- Fit-check completion rate
- Fit-check completion to scheduling-click rate
- Outbound scheduling click to booked-call rate
- Creative-specific click-through rate and landing-page view rate

Do not choose a winner on click-through rate or cheap leads alone. The winning creative and audience are the ones that produce qualified calls and paying clients at sustainable economics.

## Naming conventions

Campaign:

`PC_US_LEADS_WEBSITE_STAY-AHEAD_TEST01_2026-08`

Ad sets:

- `AS01_BROAD_US_40-65_ALL_ABO25`
- `AS02_LAL-HVC_1-3_US_40-65_ALL_ABO25`

Fallback second ad set:

- `AS02_ADV-SIGNALS_US_40-65_ALL_ABO25`

Ads:

- `AD01_STANCE_PORTRAIT_4X5_V1`
- `AD02_LIFE-BUILT_VIDEO_4X5_V1`
- `AD03_NO-BIOHACKS_TYPE_4X5_V1`

UTM content values should mirror the ad names in lowercase. Keep names stable during the test. Duplicate an ad when changing creative or copy so the original result remains interpretable.

## Launch checklist

### Offer and destination

- [ ] Doych approves the positioning, page copy, prices, and CTA.
- [ ] The `/private` page is reviewed on desktop and mobile using a Vercel preview.
- [ ] All repeated CTAs lead to the same fit check.
- [ ] The final CTA opens the correct Google scheduling page.
- [ ] The scheduling page has accurate availability, time zone, duration, and confirmation copy.
- [ ] No production deployment has occurred before explicit approval.

### Privacy and measurement

- [ ] Privacy notice accurately describes any analytics and advertising tools that will be enabled.
- [ ] Marketing tags remain off until the consent approach is approved and implemented.
- [ ] Test Events confirms event names and one-time firing.
- [ ] Network inspection confirms no fit-check answer is transmitted.
- [ ] No sensitive health, genetic, diagnosis, symptom, or free-text data is sent to Meta.
- [ ] UTMs contain campaign metadata only.
- [ ] Existing clients and booked leads are excluded where appropriate and lawful.

### Campaign build

- [ ] Objective is Leads and conversion location is Website.
- [ ] Final destination is the production `/private` URL only after Doych approves production.
- [ ] Daily test budget is explicitly approved.
- [ ] Campaign or ad-set budget method is recorded.
- [ ] Two audiences and all three creatives are present.
- [ ] Every ad has the correct primary text, headline, description, CTA, and UTM.
- [ ] Advantage+ placements are on unless a documented creative problem requires an exception.
- [ ] Comments and messages have an owner and response plan.
- [ ] Account spending limit, billing method, page identity, Instagram identity, and notification settings are verified.

### Quality control

- [ ] Copy avoids medical promises and personal-attribute language.
- [ ] Captions are present on video and readable without sound.
- [ ] Creative crops are checked at 4:5, 1:1, and 9:16.
- [ ] Page speed and mobile readability are acceptable.
- [ ] Links are tested from both Facebook and Instagram in-app browsers.
- [ ] A screenshot of every final ad and the complete Ads Manager settings is saved before launch.

### Approval gate

- [ ] Doych gives explicit approval to publish the landing page to production.
- [ ] Doych gives separate explicit approval to launch the Meta campaign and spend the agreed daily budget.

## First review cadence

- Days 1 to 3: check delivery, disapprovals, broken links, event integrity, and obvious creative failures. Avoid premature edits.
- Days 4 to 7: review spend distribution, landing-page behavior, scheduling clicks, and lead quality. Fix only clear problems.
- Days 8 to 14: pause ads that have meaningful spend with no downstream signal. Keep the test interpretable.
- Day 21: compare audiences and creatives on qualified calls and paid-client economics. Decide whether to stop, iterate, or scale gradually.

Any scale decision should use downstream quality, not lead volume alone.

## Official Meta references checked

- [Lead ads with website forms](https://www.facebook.com/business/ads/ad-objectives/lead-generation/lead-ads-with-forms)
- [Meta ad objectives](https://www.facebook.com/business/ads/ad-objectives)
- [About Conversions API](https://www.facebook.com/business/help/AboutConversionsAPI)
- [Set up and install the Meta Pixel](https://www.facebook.com/help/messenger-app/952192354843755)
- [Meta Advertising Standards](https://www.facebook.com/policies/ads/)
