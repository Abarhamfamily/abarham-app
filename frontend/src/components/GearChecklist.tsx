import React, { useState } from 'react';

const GearChecklist: React.FC = () => {
  const [checklist, setChecklist] = useState({
    'کوله‌پشتی': false,
    'کفش ترکینگ/کوهنوردی': false,
    'آب و وعده‌های غذایی': false,
    'مدارک شناسایی': false,
    'لباس مناسب فصل': false,
    'لوازم بهداشتی و کمک‌های اولیه': false,
    'تلفن همراه و پاوربانک': false,
    'کارت بانکی و پول نقد': false,
  });
  const [newItem, setNewItem] = useState('');

  const toggleItem = (item: string) => {
    setChecklist(prev => ({
      ...prev,
      [item]: !prev[item]
    }));
  };

  const addItem = () => {
    const trimmed = newItem.trim();
    if (trimmed && !checklist.hasOwnProperty(trimmed)) {
      setChecklist(prev => ({
        ...prev,
        [trimmed]: false
      }));
      setNewItem('');
    }
  };

  const deleteItem = (item: string) => {
    setChecklist(prev => {
      const newChecklist = { ...prev };
      delete newChecklist[item];
      return newChecklist;
    });
  };

  const checkedCount = Object.values(checklist).filter(v => v).length;
  const totalItems = Object.keys(checklist).length;
  const percentage = totalItems > 0 ? Math.round((checkedCount / totalItems) * 100) : 0;

  return (
    <div dir="rtl" className="p-4">
      <h2 className="mb-4">لیست چکلوازم</h2>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="progress" style={{ height: '20px' }}>
          <div className="progress-bar progress-bar-striped progress-bar-animated" role="progressbar"
            style={{ width: `${percentage}%` }} aria-valuenow={percentage} aria-valuemin="0" aria-valuemax="100">
          </div>
        </div>
        <p className="text-center mt-2">{percentage}% آماده‌سازی</p>
      </div>

      {/* Add new item */}
      <div className="input-group mb-4">
        <input
          type="text"
          className="form-control"
          placeholder="افزودن آیتم جدید..."
          value={newItem}
          onChange={e => setNewItem(e.target.value)}
        />
        <button className="btn btn-outline-secondary" type="button" onClick={addItem}>
          افزودن آیتم
        </button>
      </div>

      {/* Checklist */}
      <ul className="list-group">
        {Object.keys(checklist).map(item => (
          <li key={item} className="list-group-item d-flex justify-content-between align-items-center">
            <div className="form-check form-check-inline">
              <input
                className="form-check-input"
                type="checkbox"
                checked={checklist[item]}
                onChange={() => toggleItem(item)}
              />
              <label className="form-check-label">{item}</label>
            </div>
            <button className="btn btn-sm btn-outline-danger" onClick={() => deleteItem(item)}>
              حذف
            </button>
          </li>
        ))}
      </ul>

      {/* Status */}
      <div className="mt-3 text-center">
        <p>تأیید شده: {checkedCount}/{totalItems}</p>
      </div>
    </div>
  );
};

export default GearChecklist;