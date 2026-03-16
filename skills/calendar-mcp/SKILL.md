---
name: calendar-mcp
description: |
  MCP server for calendar management. Schedule meetings, check availability, send
  invites, and manage appointments. Integrates with Google Calendar or Outlook.
  Essential for automated meeting coordination and time management.
---

# Calendar MCP Skill

MCP server for calendar management and meeting scheduling.

## Installation

```bash
pip install mcp google-auth google-auth-oauthlib google-api-python-client
```

## Quick Reference

### Start Calendar MCP Server

```bash
# Start server
python AI_Employee_Vault/scripts/mcp-calendar/calendar_server.py

# With Google Calendar
python AI_Employee_Vault/scripts/mcp-calendar/calendar_server.py --provider google --credentials credentials.json
```

### Configure in Qwen/Claude

**File:** `~/.config/qwen-code/mcp.json`

```json
{
  "mcpServers": {
    "calendar": {
      "command": "python",
      "args": ["C:/Users/user1542/Documents/GitHub/H-0-Q4/AI_Employee_Vault/scripts/mcp-calendar/calendar_server.py"],
      "env": {
        "CALENDAR_PROVIDER": "google",
        "GOOGLE_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

### With Qwen

```bash
# Check availability
qwen "Use the calendar-mcp to check my availability tomorrow afternoon"

# Schedule meeting
qwen "Use calendar-mcp to schedule a 30-minute meeting with John next week"

# Create event
qwen "Use calendar-mcp to create an event for team meeting on Friday at 2 PM"
```

## Setup: Google Calendar API

### Step 1: Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable **Google Calendar API**
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### Step 2: Authenticate

```bash
cd AI_Employee_Vault/scripts/mcp-calendar
python authenticate.py
```

Opens browser for OAuth. Token saved automatically.

## Calendar MCP Implementation

```python
# AI_Employee_Vault/scripts/mcp-calendar/calendar_server.py
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from pathlib import Path
import os
import json

mcp = FastMCP("calendar")

# Calendar service (Google Calendar example)
def get_calendar_service():
    """Get authenticated calendar service."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    token_path = Path('calendar_token.json')
    creds_path = Path(os.environ.get('GOOGLE_CREDENTIALS', 'credentials.json'))
    
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

@mcp.tool()
async def check_availability(date: str, duration_minutes: int = 30) -> str:
    """
    Check availability on a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        duration_minutes: Required duration in minutes
    
    Returns:
        Available time slots
    """
    service = get_calendar_service()
    
    # Get events for the day
    events_result = service.events().list(
        calendarId='primary',
        timeMin=f"{date}T00:00:00Z",
        timeMax=f"{date}T23:59:59Z",
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Find free slots (simplified)
    work_start = 9  # 9 AM
    work_end = 17   # 5 PM
    
    available_slots = []
    current_hour = work_start
    
    while current_hour < work_end:
        slot_start = f"{date}T{current_hour:02d}:00:00"
        slot_end = f"{date}T{current_hour:02d}:30:00"
        
        # Check if slot conflicts with events
        conflict = False
        for event in events:
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            event_end = event['end'].get('dateTime', event['end'].get('date'))
            
            if slot_start < event_end and slot_end > event_start:
                conflict = True
                break
        
        if not conflict:
            available_slots.append(f"{current_hour:02d}:00 - {current_hour:02d}:30")
        
        current_hour += 1
    
    if available_slots:
        return f"Available slots on {date}:\n" + "\n".join(f"  - {slot}" for slot in available_slots[:5])
    return f"No available slots on {date} during work hours (9 AM - 5 PM)"

@mcp.tool()
async def schedule_meeting(title: str, date: str, time: str, duration_minutes: int = 30,
                           attendees: list = None, description: str = '') -> str:
    """
    Schedule a meeting.
    
    Args:
        title: Meeting title
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        duration_minutes: Duration in minutes
        attendees: List of attendee emails
        description: Meeting description
    
    Returns:
        Confirmation with meeting link
    """
    service = get_calendar_service()
    
    start_dt = f"{date}T{time}:00"
    end_dt = f"{date}T{int(time.split(':')[0]):02d}:{int(time.split(':')[1]) + (duration_minutes // 60)}:{duration_minutes % 60:02d}"
    
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_dt, 'timeZone': 'UTC'},
        'end': {'dateTime': end_dt, 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in (attendees or [])],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 1440},  # 1 day before
                {'method': 'popup', 'minutes': 30},    # 30 min before
            ]
        }
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    
    attendees_text = f"\nAttendees: {', '.join(attendees)}" if attendees else ""
    return f"✅ Meeting scheduled!\n\nTitle: {title}\nDate: {date} at {time}\nDuration: {duration_minutes} min{attendees_text}\n\nLink: {event.get('htmlLink', 'N/A')}"

@mcp.tool()
async def create_event(title: str, date: str, time: str, end_time: str = None,
                       location: str = '', description: str = '') -> str:
    """
    Create a calendar event.
    
    Args:
        title: Event title
        date: Date in YYYY-MM-DD format
        time: Start time in HH:MM format
        end_time: End time in HH:MM format (optional)
        location: Event location
        description: Event description
    
    Returns:
        Confirmation
    """
    service = get_calendar_service()
    
    start_dt = f"{date}T{time}:00"
    end_dt = f"{date}T{end_time.replace(':', ':')}:00" if end_time else f"{date}T{int(time.split(':')[0]) + 1:02d}:{time.split(':')[1]}:00"
    
    event = {
        'summary': title,
        'description': description,
        'location': location,
        'start': {'dateTime': start_dt, 'timeZone': 'UTC'},
        'end': {'dateTime': end_dt, 'timeZone': 'UTC'},
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Event created: {title}\n{date} at {time}\n\nLink: {event.get('htmlLink', 'N/A')}"

@mcp.tool()
async def list_events(date_from: str, date_to: str = None) -> str:
    """
    List events in date range.
    
    Args:
        date_from: Start date YYYY-MM-DD
        date_to: End date YYYY-MM-DD (default: same as from)
    
    Returns:
        List of events
    """
    service = get_calendar_service()
    
    if not date_to:
        date_to = date_from
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=f"{date_from}T00:00:00Z",
        timeMax=f"{date_to}T23:59:59Z",
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        return "No events in this date range."
    
    result = f"Events from {date_from} to {date_to}:\n\n"
    for event in events[:10]:  # Limit to 10
        start = event['start'].get('dateTime', event['start'].get('date', ''))[:16]
        result += f"• {start} - {event.get('summary', 'No title')}\n"
    
    if len(events) > 10:
        result += f"\n... and {len(events) - 10} more events"
    
    return result

@mcp.tool()
async def cancel_event(event_id: str) -> str:
    """
    Cancel/delete an event.
    
    Args:
        event_id: Google Calendar event ID
    
    Returns:
        Confirmation
    """
    service = get_calendar_service()
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"✅ Event cancelled (ID: {event_id})"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Usage Examples

### Check Availability

```bash
qwen "Use calendar-mcp to check availability on 2026-03-20 for a 60-minute meeting"
```

### Schedule Meeting

```bash
qwen "Use calendar-mcp to schedule 'Project Review' on 2026-03-21 at 14:00 for 30 minutes with john@example.com"
```

### List Events

```bash
qwen "Use calendar-mcp to list all events this week"
```

## Output Format

### Availability Response

```
Available slots on 2026-03-20:
  - 09:00 - 09:30
  - 10:00 - 10:30
  - 14:00 - 14:30
  - 15:30 - 16:00
```

### Meeting Confirmation

```
✅ Meeting scheduled!

Title: Project Review
Date: 2026-03-21 at 14:00
Duration: 30 min
Attendees: john@example.com

Link: https://calendar.google.com/event?id=xxx
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not authenticated" | Run authenticate.py first |
| "Credentials not found" | Check GOOGLE_CREDENTIALS path |
| Events not showing | Check calendar permissions |
| Can't send invites | Verify attendees have Google accounts |

## Related Skills

- `email-mcp` - Send meeting invites via email
- `notification-skill` - Send meeting reminders
- `scheduler` - Schedule recurring meetings

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
