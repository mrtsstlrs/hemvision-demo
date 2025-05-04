import React from 'react';
import logo from '/logo.png'; // положите ваш логотип (правый снизу) в src/logo.png

export default function Header() {
  return (
    <header>
      <img src={logo} alt="Hem Vision Logo" className="logo" />
      <h1>Hem Vision</h1>
    </header>
  );
}
