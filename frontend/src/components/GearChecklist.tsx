import React, { useState } from 'react';

const GearChecklist: React.FC = () => {
  const [checklist, setChecklist] = useState({
    'Backpack': false,
    'Comfortable shoes': false,
    'Food & water': false,
    'Documents (ID, tickets)': false,
    'Clothing': false,
    'Toiletries': false,
    'Phone & charger': false,
    'Money': false,
  });

  const toggleItem = (item: string) => {
    setChecklist(prev => ({
      ...prev,
      [item]: !prev[item]
    }));
  };

  const checkedCount = Object.values(checklist).filter(v => v).length;
  const totalItems = Object.keys(checklist).length;

  return (
    <div>
      <h2>Gear Checklist</h2>
      <p>Checked: {checkedCount}/{totalItems}</p>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {Object.keys(checklist).map(item => (
          <li key={item} style={{ margin: '8px 0', display: 'flex', alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={checklist[item]}
              onChange={() => toggleItem(item)}
              style={{ marginRight: '8px' }}
            />
            <label>{item}</label>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GearChecklist;