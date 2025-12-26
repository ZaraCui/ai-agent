# 📊 Google Analytics Integration Guide

## Step 1: Create Google Analytics Account

1. Go to [Google Analytics](https://analytics.google.com/)
2. Click **"Start measuring"** or **"Admin"** (if you have an account)
3. Create a new **Account** (e.g., "Travel Planning Agent")
4. Create a new **Property** (e.g., "Travel Planning Website")
5. Select **"Web"** as the platform
6. Enter your website details:
   - Website Name: Travel Planning Agent
   - Website URL: Your domain (e.g., https://yourdomain.com)
   - Industry Category: Travel
   - Reporting Time Zone: Your timezone
7. Click **"Create"** and accept the Terms of Service

## Step 2: Get Your Measurement ID

After creating the property, you'll see a **Measurement ID** in the format:
- **GA4 (Google Analytics 4)**: `G-XXXXXXXXXX`
- **Universal Analytics (deprecated)**: `UA-XXXXXXXXXX`

**Note**: Use GA4 (G-XXXXXXXXXX) as Universal Analytics is being phased out.

## Step 3: Add to Environment Variables

Add your Measurement ID to your `.env` file:

```bash
# Google Analytics
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

## Step 4: Update Flask App

The tracking code is automatically injected into your template. No changes needed to `app.py` as it already passes environment variables to templates.

## Step 5: Test Your Integration

1. **Real-time Reports**: Go to GA4 → Reports → Realtime
2. Visit your website
3. You should see your visit appear in real-time (within 30 seconds)

## Step 6: Set Up Custom Events

Google Analytics will automatically track:
- ✅ Page views
- ✅ Session duration
- ✅ User demographics

**Custom Events** (already implemented in the updated template):
- `generate_itinerary` - When user generates an itinerary
- `share_itinerary` - When user shares an itinerary
- `save_itinerary` - When user saves an itinerary
- `select_city` - When user selects a city
- `toggle_spot` - When user selects/deselects spots
- `user_signup` - When user creates an account
- `user_signin` - When user logs in

## Step 7: View Reports

### Realtime Reports
- **Reports → Realtime** - See active users now

### Engagement Reports
- **Reports → Engagement → Events** - See all tracked events
- **Reports → Engagement → Pages and screens** - Most visited pages

### User Reports
- **Reports → User → Demographics** - Age, gender, interests
- **Reports → User → Tech** - Browser, device, OS

### Acquisition Reports
- **Reports → Acquisition → Traffic acquisition** - Where users come from

## Step 8: Set Up Conversion Goals

1. Go to **Admin → Events**
2. Click **"Create event"**
3. Mark important events as **conversions**:
   - `generate_itinerary` → Mark as conversion
   - `save_itinerary` → Mark as conversion
   - `user_signup` → Mark as conversion

## Step 9: Advanced Features (Optional)

### A. Enhanced Ecommerce (for future monetization)
```javascript
gtag('event', 'purchase', {
  transaction_id: 'T12345',
  value: 9.99,
  currency: 'USD',
  items: [{
    item_id: 'pro_subscription',
    item_name: 'Pro Subscription',
    price: 9.99,
    quantity: 1
  }]
});
```

### B. User Properties
```javascript
gtag('set', 'user_properties', {
  user_type: 'premium',
  favorite_destination: 'Paris'
});
```

### C. Custom Dimensions
Set up custom dimensions in GA4 Admin to track:
- Transport mode preference
- Average trip duration
- Number of cities visited

## Troubleshooting

### Issue: No data showing up
**Solutions:**
1. Check that your Measurement ID is correct in `.env`
2. Clear browser cache and try again
3. Check browser console for errors
4. Disable ad blockers (they block GA)
5. Wait 24-48 hours for data to populate (realtime should work immediately)

### Issue: Events not tracking
**Solutions:**
1. Check browser console for GA errors
2. Use [GA Debugger Chrome Extension](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna)
3. Verify gtag function is available: Type `gtag` in browser console

### Issue: Duplicate tracking
**Solutions:**
1. Make sure you only have ONE GA snippet in your HTML
2. Check that you're not including GA code multiple times

## Privacy & GDPR Compliance

### Add Cookie Consent Banner

**Important**: If you have EU users, you need cookie consent before loading GA.

1. Add a cookie consent library like [Cookie Consent](https://www.cookieconsent.com/)
2. Only load GA after user consent:

```javascript
// Wait for consent before initializing GA
if (getCookieConsent()) {
  loadGoogleAnalytics();
}
```

### Anonymize IP Addresses

GA4 automatically anonymizes IPs, but you can enhance privacy:

```javascript
gtag('config', 'G-XXXXXXXXXX', {
  'anonymize_ip': true,
  'allow_google_signals': false,
  'allow_ad_personalization_signals': false
});
```

### Update Privacy Policy

Add to your Privacy Policy:
- What data is collected (page views, events, demographics)
- How it's used (improve user experience, analytics)
- Third-party services (Google Analytics)
- User rights (opt-out, data deletion)
- Cookie usage

## Best Practices

1. ✅ **Track meaningful events** - Focus on business-critical actions
2. ✅ **Use descriptive names** - `generate_itinerary` not `button_click`
3. ✅ **Add event parameters** - Include context (city, transport_mode)
4. ✅ **Set up conversion goals** - Know what success looks like
5. ✅ **Review reports weekly** - Make data-driven decisions
6. ✅ **Respect user privacy** - Implement cookie consent
7. ✅ **Don't track sensitive data** - No PII (emails, names) in events

## Useful Resources

- [GA4 Documentation](https://support.google.com/analytics/answer/10089681)
- [GA4 Event Reference](https://developers.google.com/analytics/devguides/collection/ga4/events)
- [GA4 Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [Google Tag Assistant](https://tagassistant.google.com/)

## Next Steps

After setting up GA, consider:
1. **Google Search Console** - Track SEO performance
2. **Google Tag Manager** - Manage all tracking tags in one place
3. **Hotjar or Microsoft Clarity** - Heatmaps and session recordings
4. **Mixpanel or Amplitude** - Product analytics with cohort analysis

---

## Quick Reference: Event Tracking Code

```javascript
// Basic event
gtag('event', 'event_name', {
  'category': 'engagement',
  'label': 'user_action'
});

// Event with parameters
gtag('event', 'generate_itinerary', {
  'city': 'Paris',
  'days': 3,
  'transport_mode': 'transit',
  'value': 1
});

// E-commerce purchase
gtag('event', 'purchase', {
  'transaction_id': 'T123',
  'value': 29.99,
  'currency': 'USD'
});
```

Happy tracking! 📊
