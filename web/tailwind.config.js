/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        flat: {
          turquoise: '#1abc9c',
          greenSea: '#16a085',
          emerald: '#2ecc71',
          nephritis: '#27ae60',
          peterRiver: '#3498db',
          belizeHole: '#2980b9',
          amethyst: '#9b59b6',
          wisteria: '#8e44ad',
          wetAsphalt: '#34495e',
          midnightBlue: '#2c3e50',
          sunFlower: '#f1c40f',
          orange: '#f39c12',
          carrot: '#e67e22',
          pumpkin: '#d35400',
          alizarin: '#e74c3c',
          pomegranate: '#c0392b',
          clouds: '#ecf0f1',
          silver: '#bdc3c7',
          concrete: '#95a5a6',
          asbestos: '#7f8c8d',
        }
      },
      boxShadow: {
        'flat': '3px 3px 0px 0px rgba(44, 62, 80, 0.9)',
        'flat-sm': '2px 2px 0px 0px rgba(44, 62, 80, 0.8)',
        'flat-lg': '5px 5px 0px 0px rgba(44, 62, 80, 0.9)',
        'flat-pressed': '1px 1px 0px 0px rgba(44, 62, 80, 0.9)',
        'flat-primary': '3px 3px 0px 0px #16a085',
        'flat-danger': '3px 3px 0px 0px #c0392b',
        'flat-accent': '3px 3px 0px 0px #2980b9',
      }
    },
  },
  plugins: [],
}
