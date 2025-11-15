# NeuraCity Frontend Documentation

## Overview
Complete React frontend application for the NeuraCity smart city platform, built with Vite, TailwindCSS, and React Router.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ImageUpload.jsx      # Drag & drop image upload with preview
│   │   ├── GPSCapture.jsx       # Browser geolocation capture
│   │   ├── IssueForm.jsx        # Complete issue reporting form
│   │   ├── Map2D.jsx            # Leaflet map wrapper with layers
│   │   ├── RouteCard.jsx        # Route information display
│   │   ├── NoiseLegend.jsx      # Noise level legend
│   │   ├── MoodLegend.jsx       # Mood score legend
│   │   ├── WorkOrderCard.jsx    # Work order display with approval
│   │   └── Navbar.jsx           # Main navigation bar
│   ├── pages/               # Page components
│   │   ├── Home.jsx             # Landing page with feature overview
│   │   ├── ReportIssue.jsx      # Issue reporting page
│   │   ├── PlanRoute.jsx        # Smart routing page
│   │   ├── MoodMap.jsx          # City mood visualization
│   │   └── Admin.jsx            # Admin dashboard
│   ├── lib/                 # Utilities and API client
│   │   ├── api.js               # Axios-based API client
│   │   └── helpers.js           # Utility functions
│   ├── App.jsx              # Main app component with routing
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles + Leaflet CSS
├── .env                     # Environment variables
├── package.json             # Dependencies
└── vite.config.js          # Vite configuration
```

## Installation & Setup

### 1. Install Dependencies
```bash
cd C:\Users\mianm\Downloads\NeuraCity\frontend
npm install
```

### 2. Configure Environment
Create a `.env` file with:
```
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### 4. Build for Production
```bash
npm run build
```

Built files will be in the `dist` folder.

## Core Features

### 1. Issue Reporting (C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\ReportIssue.jsx)

**User Flow:**
1. User navigates to `/report`
2. Upload image (REQUIRED) - drag & drop or click to select
3. Capture GPS location (REQUIRED) - browser geolocation API
4. Select issue type (REQUIRED):
   - Accident
   - Pothole
   - Traffic Light
   - Other (requires text specification)
5. Optionally add description
6. Submit form
7. See confirmation with severity, urgency, priority scores
8. Auto-redirect to home after 5 seconds

**Components Used:**
- `ImageUpload` - Handles image selection with preview
- `GPSCapture` - Captures browser geolocation
- `IssueForm` - Combines all inputs with validation

**API Call:**
```javascript
reportIssue(formData) // FormData with image, lat, lng, issue_type, description
```

**Success Response:**
```json
{
  "id": "uuid",
  "issue_type": "pothole",
  "severity": 0.75,
  "urgency": 0.60,
  "priority": "high",
  "action_type": "work_order",
  "status": "open"
}
```

### 2. Route Planning (C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\PlanRoute.jsx)

**User Flow:**
1. User navigates to `/route`
2. Click map to set origin (green marker appears)
3. Click map to set destination (red marker appears)
4. Select route type:
   - **Drive** - Fastest route avoiding accidents
   - **Eco Drive** - Low emissions, avoids congestion
   - **Quiet Walk** - Minimizes noise exposure
5. Click "Plan Route"
6. Route drawn on map with polyline
7. Route details displayed:
   - ETA
   - Distance
   - CO₂ score (Eco) or Noise score (Quiet Walk)
   - AI-generated explanation

**Components Used:**
- `Map2D` - Interactive map with click handler
- `RouteCard` - Displays route information

**API Call:**
```javascript
planRoute(origin, destination, routeType)
```

**Example Response:**
```json
{
  "path": [{"lat": 37.7749, "lng": -122.4194}, ...],
  "distance": 2500, // meters
  "eta": 600, // seconds
  "route_type": "quiet_walk",
  "noise_score": 52.5, // dB
  "explanation": "This route uses quiet side streets..."
}
```

### 3. Mood Map (C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\MoodMap.jsx)

**User Flow:**
1. User navigates to `/mood`
2. Map loads with colored circles representing city areas
3. Colors indicate mood:
   - Green: Positive (0.5 to 1.0)
   - Yellow: Neutral (0 to 0.5)
   - Red: Negative (-1.0 to 0)
4. Click area for details (mood score, post count)
5. Sidebar shows area statistics and list

**Components Used:**
- `Map2D` - Displays mood area circles
- `MoodLegend` - Color legend

**API Call:**
```javascript
getMoodData()
```

**Example Response:**
```json
[
  {
    "id": "uuid",
    "area_id": "MIDTOWN",
    "lat": 37.7749,
    "lng": -122.4194,
    "mood_score": 0.65,
    "post_count": 150
  }
]
```

### 4. Admin Dashboard (C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\Admin.jsx)

**Three Tabs:**

#### Emergency Queue Tab
- Lists accident reports
- Shows AI-generated Gemini summaries
- "Mark as Reviewed" button
- Status: pending → reviewed

**API Call:**
```javascript
getEmergencyQueue()
```

**Example Response:**
```json
[
  {
    "id": "uuid",
    "issue_id": "uuid",
    "summary": "Multi-vehicle collision at intersection...",
    "status": "pending",
    "issue": { /* full issue object */ }
  }
]
```

#### Work Orders Tab
- Lists auto-generated work orders
- Shows Gemini-suggested materials
- Shows assigned contractor
- "Approve Work Order" button
- Status: pending_review → approved

**Components Used:**
- `WorkOrderCard` - Displays work order with approval

**API Call:**
```javascript
getWorkOrders()
approveWorkOrder(id)
```

#### All Issues Tab
- Table of all reported issues
- Filterable by status
- Dropdown to update status (open/in_progress/resolved)
- View image link
- Shows priority, location, date

**API Call:**
```javascript
getIssues(filters)
updateIssueStatus(id, status)
```

## API Client (C:\Users\mianm\Downloads\NeuraCity\frontend\src\lib\api.js)

### Configuration
```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' }
});
```

### Available Functions

| Function | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| `reportIssue(formData)` | POST | `/issues` | Submit new issue with image |
| `getIssues(filters)` | GET | `/issues` | Get all issues |
| `updateIssueStatus(id, status)` | PATCH | `/issues/{id}` | Update issue status |
| `getMoodData()` | GET | `/mood` | Get mood areas |
| `getTrafficData()` | GET | `/traffic` | Get traffic segments |
| `getNoiseData()` | GET | `/noise` | Get noise segments |
| `planRoute(origin, dest, type)` | POST | `/plan` | Plan route |
| `getEmergencyQueue()` | GET | `/admin/emergency` | Get emergencies |
| `getWorkOrders()` | GET | `/admin/work-orders` | Get work orders |
| `approveWorkOrder(id)` | POST | `/admin/work-orders/{id}/approve` | Approve work order |
| `markEmergencyReviewed(id)` | PATCH | `/admin/emergency/{id}` | Mark emergency reviewed |

### Error Handling
All API functions use a centralized error handler that:
- Catches server errors (response.data.detail)
- Catches network errors
- Throws user-friendly error messages

## Components Reference

### ImageUpload (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\ImageUpload.jsx)

**Props:**
- `onImageSelect(file)` - Callback when image selected
- `required` - Boolean, shows asterisk if true

**Features:**
- Drag & drop support
- Click to browse
- Image preview
- Remove image button
- File type validation (images only)

**Usage:**
```jsx
<ImageUpload
  onImageSelect={(file) => setImage(file)}
  required
/>
```

### GPSCapture (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\GPSCapture.jsx)

**Props:**
- `onLocationCapture(coords)` - Callback with {lat, lng}
- `required` - Boolean, shows asterisk if true

**Features:**
- Uses browser Geolocation API
- High accuracy mode
- Shows latitude/longitude when captured
- Recapture option
- Error handling with user-friendly messages

**Usage:**
```jsx
<GPSCapture
  onLocationCapture={(coords) => setLocation(coords)}
  required
/>
```

### Map2D (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\Map2D.jsx)

**Props:**
- `center` - [lat, lng] array for map center
- `zoom` - Number, zoom level (default: 13)
- `height` - String, CSS height (default: '500px')
- `onMapClick(coords)` - Callback when map clicked
- `issues` - Array of issue objects to display as markers
- `moodAreas` - Array of mood areas to display as circles
- `noiseSegments` - Array of noise data for heatmap
- `trafficSegments` - Array of traffic data
- `route` - Route object with path array
- `markers` - Array of custom markers {lat, lng, label, color}

**Features:**
- OpenStreetMap tiles
- Multiple layer support
- Custom colored markers
- Popup information on click
- Auto-fit bounds to route

**Usage:**
```jsx
<Map2D
  height="600px"
  onMapClick={(coords) => handleClick(coords)}
  issues={issuesData}
  moodAreas={moodData}
  route={routeData}
  markers={[
    {lat: 37.7749, lng: -122.4194, label: 'Start', color: '#10b981'}
  ]}
/>
```

### RouteCard (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\RouteCard.jsx)

**Props:**
- `route` - Route object from API

**Displays:**
- ETA (formatted as hours/minutes)
- Distance (km or meters)
- CO₂ score (for eco routes)
- Noise score (for quiet walk routes)
- AI explanation
- Route type badge

### WorkOrderCard (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\WorkOrderCard.jsx)

**Props:**
- `workOrder` - Work order object
- `onApprove(id)` - Callback when approved

**Displays:**
- Issue type and location
- Material suggestions from Gemini
- Contractor information (name, specialty, contact)
- Status badge
- Approve button (if pending)

### Navbar (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\Navbar.jsx)

**Features:**
- Logo and branding
- Navigation links with icons
- Active route highlighting
- Responsive design
- Mobile menu (basic implementation)

**Routes:**
- Home (/)
- Report Issue (/report)
- Plan Route (/route)
- Mood Map (/mood)
- Admin (/admin)

## Utility Functions (C:\Users\mianm\Downloads\NeuraCity\frontend\src\lib\helpers.js)

### Color Functions
```javascript
getMoodColor(moodScore)      // Returns hex color based on mood
getNoiseColor(noiseDb)       // Returns hex color based on noise level
getTrafficColor(congestion)  // Returns hex color based on traffic
getPriorityColor(priority)   // Returns hex color based on priority
```

### Formatting Functions
```javascript
formatDate(dateString)         // "Jan 15, 2025, 3:45 PM"
formatDistance(meters)         // "2.5 km" or "500 m"
formatDuration(seconds)        // "1h 30m" or "45m"
formatIssueType(issueType)     // "traffic_light" → "Traffic Light"
```

### Label Functions
```javascript
getNoiseLabel(noiseDb)      // "Quiet", "Moderate", or "Loud"
getMoodLabel(moodScore)     // "Positive", "Neutral", or "Negative"
```

### Validation
```javascript
isValidCoordinates(lat, lng)  // Validates GPS coordinates
```

## Styling

### TailwindCSS Configuration
Primary color palette (blue):
- 50: #f0f9ff
- 100: #e0f2fe
- 200: #bae6fd
- 300: #7dd3fc
- 400: #38bdf8
- 500: #0ea5e9
- 600: #0284c7 (primary)
- 700: #0369a1
- 800: #075985
- 900: #0c4a6e

### Custom CSS
- Leaflet container styles
- Custom marker styles (no default styling)

## Testing Workflows

### 1. Report Issue Workflow
```
1. Navigate to /report
2. Upload any image file (JPG, PNG)
3. Click "Capture GPS Location"
4. Allow browser location access
5. Verify coordinates appear
6. Select "Pothole" from dropdown
7. Add description: "Large pothole on Main St"
8. Click "Submit Issue Report"
9. Verify success page shows severity/urgency/priority
10. Wait for auto-redirect or click "Return Home"
```

### 2. Plan Route Workflow
```
1. Navigate to /route
2. Click map to set origin (green "Start" marker appears)
3. Click different location for destination (red "End" marker)
4. Select "Quiet Walk" radio button
5. Click "Plan Route"
6. Verify blue route line appears
7. Verify RouteCard shows ETA, distance, noise score
8. Click "Reset Points" to start over
```

### 3. View Mood Map Workflow
```
1. Navigate to /mood
2. Verify colored circles appear on map
3. Click on a circle to see popup with mood details
4. Check sidebar for area statistics
5. Verify legend matches colors
6. Click "Refresh" to reload data
```

### 4. Admin Workflow
```
Emergency Queue:
1. Navigate to /admin
2. Click "Emergency Queue" tab
3. View AI summaries
4. Click "Mark as Reviewed"
5. Verify status changes to "REVIEWED"

Work Orders:
1. Click "Work Orders" tab
2. Review material suggestions
3. Check contractor assignment
4. Click "Approve Work Order"
5. Verify status changes to "APPROVED"

All Issues:
1. Click "All Issues" tab
2. View table of all issues
3. Change status dropdown (open → in_progress)
4. Click "View Image" to see uploaded photo
5. Verify status update
```

## Browser Compatibility

### Tested Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Required Browser Features
- Geolocation API
- File API
- Drag & Drop API
- ES6+ JavaScript
- CSS Grid & Flexbox

## Performance Considerations

### Image Upload
- Client-side preview only (no upload until submit)
- FormData for multipart uploads
- File size validation recommended (add in production)

### Map Rendering
- Lazy loading of map tiles
- Layer groups for efficient rendering
- Clear layers before re-rendering

### API Calls
- Error handling with user feedback
- Loading states for all async operations
- Automatic retry not implemented (add in production)

## Known Limitations

1. **No Authentication**: Admin routes are publicly accessible
2. **No Offline Support**: Requires active internet connection
3. **No Image Compression**: Large images sent as-is
4. **Basic Mobile Menu**: Not fully functional
5. **No Real-time Updates**: Manual refresh required
6. **No Pagination**: All data loaded at once
7. **No Search/Filter**: Limited filtering capabilities

## Future Enhancements

1. User authentication and authorization
2. Real-time updates with WebSockets
3. Advanced filtering and search
4. Image compression before upload
5. Offline support with service workers
6. Push notifications for admins
7. Export data functionality
8. Multi-language support
9. Accessibility improvements (WCAG 2.1 AA)
10. Advanced map features (clustering, custom tiles)

## Deployment

### Environment Variables for Production
```
VITE_API_URL=https://api.neuracity.com/api/v1
```

### Build Command
```bash
npm run build
```

### Deploy to Vercel
```bash
vercel --prod
```

### Deploy to Netlify
```bash
netlify deploy --prod --dir=dist
```

## Troubleshooting

### Issue: Map not displaying
- Check Leaflet CSS is imported in index.css
- Verify map container has height
- Check browser console for errors

### Issue: GPS not working
- Ensure HTTPS or localhost (required for Geolocation API)
- Check browser permissions
- Try different browser

### Issue: Image upload fails
- Verify backend accepts multipart/form-data
- Check CORS configuration
- Ensure FormData correctly constructed

### Issue: API calls fail
- Verify backend is running on correct port
- Check VITE_API_URL in .env
- Check network tab for error details
- Verify CORS headers on backend

## File Paths Reference

All file paths in this project (absolute paths for Windows):

**Components:**
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\ImageUpload.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\GPSCapture.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\IssueForm.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\Map2D.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\RouteCard.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\NoiseLegend.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\MoodLegend.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\WorkOrderCard.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\Navbar.jsx`

**Pages:**
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\Home.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\ReportIssue.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\PlanRoute.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\MoodMap.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\Admin.jsx`

**Library:**
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\lib\api.js`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\lib\helpers.js`

**Configuration:**
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\App.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\main.jsx`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\src\index.css`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\.env`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\package.json`
- `C:\Users\mianm\Downloads\NeuraCity\frontend\vite.config.js`

## Support

For issues or questions, refer to:
- Project roadmap: `C:\Users\mianm\Downloads\NeuraCity\roadmap.md`
- Project context: `C:\Users\mianm\Downloads\NeuraCity\context-neuracity-2025-11-14.md`
