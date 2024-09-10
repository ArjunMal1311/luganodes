import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

function App() {
  const [deposits, setDeposits] = useState([]);

  useEffect(() => {
    const fetchDeposits = async () => {
      const result = await axios.get('http://localhost:5000/api/deposits');
      setDeposits(result.data);
    };

    fetchDeposits();
    const interval = setInterval(fetchDeposits, 15000); 

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <h1>Ethereum Deposit Tracker</h1>
      <table>
        <thead>
          <tr>
            <th>Block Number</th>
            <th>Timestamp</th>
            <th>Transaction Hash</th>
            <th>Public Key</th>
          </tr>
        </thead>
        <tbody>
          {deposits.map((deposit, index) => (
            <tr key={index}>
              <td>{deposit.blockNumber}</td>
              <td>{deposit.blockTimestamp}</td>
              <td>{deposit.hash}</td>
              <td>{deposit.pubkey}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;