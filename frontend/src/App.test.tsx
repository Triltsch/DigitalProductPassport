/**
 * Purpose: Verifies the frontend foundation renders and exposes the planned
 * feature-slice placeholders so sprint follow-up tickets can build on a stable shell.
 */

import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  /**
   * Verifies that the foundation headline and at least one expected feature-slice
   * entry are visible after initial render.
   */
  it("renders the foundation shell and feature slices", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: /digital product passport/i })
    ).toBeInTheDocument();
    expect(screen.getByText("dashboard")).toBeInTheDocument();
  });
});