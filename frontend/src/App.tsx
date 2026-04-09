const featureSlices = [
  "dashboard",
  "dpp",
  "submodels",
  "lifecycle",
  "certifications",
  "workflows",
  "access-management",
  "import-export",
  "admin",
  "public-dpp",
];

function App() {
  return (
    <main className="app-shell" aria-label="Digital Product Passport frontend foundation">
      <section className="card">
        <h1>Digital Product Passport</h1>
        <p>
          Frontend foundation initialized with React, TypeScript, Vite, ESLint, Prettier, and
          Vitest.
        </p>
        <h2>Planned Feature Slices</h2>
        <ul>
          {featureSlices.map((slice) => (
            <li key={slice}>{slice}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}

export default App;