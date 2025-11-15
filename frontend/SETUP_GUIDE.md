# NeuraCity Frontend - Quick Setup Guide

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

### Step 1: Install Dependencies
```bash
cd C:\Users\mianm\Downloads\NeuraCity\frontend
npm install
```

### Step 2: Configure Environment
The `.env` file is already configured with defaults:
```
VITE_API_URL=http://localhost:8000/api/v1
```

If your backend runs on a different URL, update this file.

### Step 3: Start Development Server
```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### Step 4: Verify Backend Connection
The frontend expects the backend API to be running at:
```
http://localhost:8000/api/v1
```

Make sure your FastAPI backend is running before testing API-dependent features.

## Quick Start - Test Each Feature

### 1. Home Page
- Navigate to `http://localhost:5173`
- You should see the NeuraCity landing page with 4 feature cards
- System status indicator should show "Online"

### 2. Report Issue
1. Click "Report Issues" or navigate to `/report`
2. Upload an image (drag & drop or click)
3. Click "Capture GPS Location" and allow browser location access
4. Select issue type (e.g., "Pothole")
5. Optionally add description
6. Click "Submit Issue Report"
7. **Note**: This will fail without a running backend, but you can test the UI

### 3. Plan Route
1. Click "Smart Routing" or navigate to `/route`
2. Click anywhere on the map to set origin (green "Start" marker)
3. Click another location to set destination (red "End" marker)
4. Select route type (Drive, Eco Drive, or Quiet Walk)
5. Click "Plan Route"
6. **Note**: Route will only appear if backend is running

### 4. Mood Map
1. Click "City Mood" or navigate to `/mood`
2. Map should load with colored circles (if backend has mood data)
3. Click circles for details
4. Sidebar shows statistics

### 5. Admin Dashboard
1. Click "Admin Portal" or navigate to `/admin`
2. Three tabs available:
   - Emergency Queue
   - Work Orders
   - All Issues
3. Each tab loads data from backend

## Testing Without Backend

You can test the UI components without a backend:

### Image Upload
- Visit `/report`
- Upload image works fully client-side
- Preview displays correctly

### GPS Capture
- Visit `/report`
- Click "Capture GPS Location"
- Should work if browser has location access

### Map Display
- Visit `/route` or `/mood`
- Map should load with OpenStreetMap tiles
- Click events work
- Markers can be placed on `/route`

### Navigation
- All navigation links work
- Active page highlighting works
- Responsive design can be tested by resizing browser

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Project Structure Overview

```
src/
├── components/    # 9 reusable components
├── pages/         # 5 page components
├── lib/           # API client + helpers
├── App.jsx        # Main routing
└── index.css      # Global styles
```

## Key Files Created

### Components (C:\Users\mianm\Downloads\NeuraCity\frontend\src\components\)
1. **ImageUpload.jsx** - Image upload with drag & drop
2. **GPSCapture.jsx** - Browser geolocation capture
3. **IssueForm.jsx** - Complete issue reporting form
4. **Map2D.jsx** - Leaflet map with multiple layers
5. **RouteCard.jsx** - Route information display
6. **NoiseLegend.jsx** - Noise level legend
7. **MoodLegend.jsx** - Mood score legend
8. **WorkOrderCard.jsx** - Work order with approval
9. **Navbar.jsx** - Main navigation

### Pages (C:\Users\mianm\Downloads\NeuraCity\frontend\src\pages\)
1. **Home.jsx** - Landing page
2. **ReportIssue.jsx** - Issue reporting
3. **PlanRoute.jsx** - Smart routing
4. **MoodMap.jsx** - City mood visualization
5. **Admin.jsx** - Admin dashboard with 3 tabs

### Library (C:\Users\mianm\Downloads\NeuraCity\frontend\src\lib\)
1. **api.js** - Axios API client with 11 functions
2. **helpers.js** - Utility functions for colors, formatting, validation

## API Integration

All API calls go through `src/lib/api.js`:

```javascript
import { reportIssue, getIssues, planRoute, getMoodData, ... } from './lib/api';

// Example: Report issue
const formData = new FormData();
formData.append('image', imageFile);
formData.append('lat', 37.7749);
formData.append('lng', -122.4194);
formData.append('issue_type', 'pothole');

const result = await reportIssue(formData);
```

## Styling

### TailwindCSS
- All components use Tailwind utility classes
- Primary color: Blue (#0284c7)
- Responsive design with mobile-first approach

### Custom Styles
- Leaflet CSS imported in `index.css`
- Custom marker styles for map
- Loading spinners
- Form validation feedback

## User Workflows Implemented

### Report Issue Flow
```
Upload Image (required)
  → Capture GPS (required)
  → Select Type (required)
  → Add Description (optional)
  → Submit
  → See Confirmation
  → Auto-redirect
```

### Plan Route Flow
```
Click map for origin
  → Click map for destination
  → Select route type
  → Plan route
  → View route on map
  → See route details
```

### View Mood Flow
```
Load mood data
  → Display colored areas
  → Click for details
  → View statistics
```

### Admin Flow
```
Select tab (Emergency/Work Orders/Issues)
  → View list
  → Take action (review/approve/update status)
```

## Browser Requirements

### Required Features
- Geolocation API (for GPS capture)
- File API (for image upload)
- ES6+ JavaScript
- CSS Grid & Flexbox

### Tested Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Map not showing
- Check browser console for errors
- Verify Leaflet CSS is loaded (check Network tab)
- Ensure map container has height set

### GPS not working
- Must be on HTTPS or localhost
- Check browser location permissions
- Try in different browser

### API calls fail
- Verify backend is running
- Check `.env` has correct API URL
- Open Network tab to see actual request
- Check CORS headers on backend

### Images not uploading
- Check file size (large files may timeout)
- Verify backend accepts multipart/form-data
- Check browser console for errors

## Next Steps

### Before Testing with Backend
1. Ensure backend is running on port 8000
2. Verify database has sample data
3. Check CORS is configured correctly
4. Test each API endpoint individually

### Production Deployment
1. Update `.env` with production API URL
2. Run `npm run build`
3. Deploy `dist` folder to Vercel/Netlify
4. Configure environment variables on hosting platform

## Component Usage Examples

### Using ImageUpload
```jsx
import ImageUpload from '../components/ImageUpload';

const [image, setImage] = useState(null);

<ImageUpload
  onImageSelect={(file) => setImage(file)}
  required
/>
```

### Using GPSCapture
```jsx
import GPSCapture from '../components/GPSCapture';

const [location, setLocation] = useState(null);

<GPSCapture
  onLocationCapture={(coords) => setLocation(coords)}
  required
/>
```

### Using Map2D
```jsx
import Map2D from '../components/Map2D';

<Map2D
  height="600px"
  center={[37.7749, -122.4194]}
  zoom={13}
  onMapClick={(coords) => console.log(coords)}
  issues={issuesData}
  moodAreas={moodData}
  route={routeData}
  markers={[
    {lat: 37.7749, lng: -122.4194, label: 'Start', color: '#10b981'}
  ]}
/>
```

## Available Scripts

```json
{
  "dev": "vite",              // Start dev server
  "build": "vite build",       // Build for production
  "preview": "vite preview",   // Preview production build
  "lint": "eslint . --ext js,jsx"  // Run linter
}
```

## Dependencies Installed

### Production Dependencies
- react 18.2.0
- react-dom 18.2.0
- react-router-dom 6.20.0
- leaflet 1.9.4
- react-leaflet 4.2.1
- axios 1.6.2
- lucide-react 0.294.0
- clsx 2.0.0
- tailwind-merge 2.1.0

### Development Dependencies
- vite 5.0.8
- @vitejs/plugin-react 4.2.1
- tailwindcss 3.3.6
- autoprefixer 10.4.16
- postcss 8.4.32
- eslint 8.55.0

## Performance Tips

1. **Image Upload**: Consider adding client-side compression
2. **Map Rendering**: Clear layers before adding new data
3. **API Calls**: Add debouncing for rapid requests
4. **Large Lists**: Implement pagination (not currently present)

## Security Considerations

1. **No Authentication**: Admin routes are public
2. **Input Validation**: Add server-side validation
3. **XSS Protection**: Sanitize user inputs
4. **CSRF**: Add CSRF tokens for state-changing operations

## Accessibility

Current implementation:
- Semantic HTML elements
- Keyboard navigation (basic)
- Color contrast (meets WCAG AA)
- Alt text needed for images

Improvements needed:
- ARIA labels
- Screen reader testing
- Focus management
- Keyboard shortcuts

## Mobile Responsiveness

All pages are mobile-responsive with:
- Tailwind's responsive breakpoints
- Mobile-first design approach
- Touch-friendly tap targets
- Responsive navigation (basic implementation)

## Documentation

Full documentation available at:
- `C:\Users\mianm\Downloads\NeuraCity\frontend\FRONTEND_DOCUMENTATION.md`

Quick reference:
- Setup guide: This file
- Project roadmap: `C:\Users\mianm\Downloads\NeuraCity\roadmap.md`
- Context: `C:\Users\mianm\Downloads\NeuraCity\context-neuracity-2025-11-14.md`

## Support & Contact

For questions or issues:
1. Check the full documentation
2. Review the project roadmap
3. Inspect browser console for errors
4. Verify backend API is running correctly

---

**Created**: November 14, 2025
**Frontend Developer**: Claude (NeuraCity Frontend Specialist)
**Status**: Complete and ready for integration with backend
