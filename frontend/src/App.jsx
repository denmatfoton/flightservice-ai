
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import './App.css';

function App() {
  const [form, setForm] = useState({
    pilotName: '',
    pilotQualifications: '',
    flightRules: 'VFR',
    aircraftType: '',
    aircraftEquipment: '',
    trueAirspeed: '',
    departureAirport: '',
    destinationAirport: '',
    takeoffTime: '',
    estimatedEnroute: '',
    alternateAirports: '',
  });
  
  const [flightData, setFlightData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/flight', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });
      const result = await response.json();
      if (result.status === 'success') {
        setFlightData(result.flight_info);
      } else {
        alert('Submission failed.');
      }
    } catch (error) {
      alert('Error submitting flight information.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flight-form-container">
      <h1>Artificial Flight Service</h1>
      <form className="flight-form" onSubmit={handleSubmit}>
        <fieldset>
          <legend>Pilot and Flight Rules</legend>
          <label>
            Pilot's Name:
            <input type="text" name="pilotName" value={form.pilotName} onChange={handleChange} required />
          </label>
          <label>
            Pilot Qualifications:
            <input type="text" name="pilotQualifications" value={form.pilotQualifications} onChange={handleChange} required />
          </label>
          <label>
            Flight Rules:
            <select name="flightRules" value={form.flightRules} onChange={handleChange} required>
              <option value="VFR">VFR</option>
              <option value="IFR">IFR</option>
            </select>
          </label>
        </fieldset>
        <fieldset>
          <legend>Aircraft & Performance</legend>
          <label>
            Aircraft Type:
            <input type="text" name="aircraftType" value={form.aircraftType} onChange={handleChange} required />
          </label>
          <label>
            Aircraft Equipment:
            <input type="text" name="aircraftEquipment" value={form.aircraftEquipment} onChange={handleChange} required />
          </label>
          <label>
            True Airspeed:
            <input type="number" name="trueAirspeed" value={form.trueAirspeed} onChange={handleChange} required />
          </label>
        </fieldset>
        <fieldset>
          <legend>Route & Timing</legend>
          <label>
            Departure Airport:
            <input type="text" name="departureAirport" value={form.departureAirport} onChange={handleChange} required />
          </label>
          <label>
            Destination Airport:
            <input type="text" name="destinationAirport" value={form.destinationAirport} onChange={handleChange} required />
          </label>
          <label>
            Planned Takeoff Time:
            <input type="datetime-local" name="takeoffTime" value={form.takeoffTime} onChange={handleChange} required />
          </label>
          <label>
            Estimated Time En Route:
            <input type="text" name="estimatedEnroute" value={form.estimatedEnroute} onChange={handleChange} required placeholder="e.g. 2h 30m" />
          </label>
          <label>
            Alternate Airports:
            <input type="text" name="alternateAirports" value={form.alternateAirports} onChange={handleChange} />
          </label>
        </fieldset>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Submit Flight Info'}
        </button>
      </form>
      
      {flightData && (
        <div className="flight-data-container">
          <h2>AI Flight Briefing</h2>
          <div className="markdown-briefing">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeSanitize]}
              components={{
                h1: (props) => <h2 {...props} />,
                h2: (props) => <h3 {...props} />,
                table: (props) => <table className="md-table" {...props} />,
                code: ({inline, className, children, ...rest}) => (
                  inline
                    ? <code className="inline-code" {...rest}>{children}</code>
                    : <pre className="code-block"><code {...rest}>{children}</code></pre>
                )
              }}
            >
              {flightData.ai_analysis?.briefing || 'No briefing available.'}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
