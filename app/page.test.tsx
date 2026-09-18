import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import Home from "./page";

describe("setup experience", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => cleanup());

  it("renders the complete setup controls after hydration", async () => {
    render(<Home />);
    await waitFor(() => expect(screen.getByRole("heading", { name: "Build a practice set" })).toBeInTheDocument());
    expect(screen.getByRole("slider", { name: /Question count/ })).toHaveValue("10");
    expect(screen.getByRole("radio", { name: /Curated only/ })).toBeChecked();
    expect(screen.getByRole("button", { name: /Start practice/ })).toBeEnabled();
    expect(screen.getByText(/Not affiliated with or endorsed by ABO-NCLE/)).toBeInTheDocument();
  });

  it("ignores malformed persisted state and keeps setup usable", async () => {
    localStorage.setItem("opticprep.settings.v1", JSON.stringify({ count: "many" }));
    localStorage.setItem("opticprep.session.v1", JSON.stringify({ phase: "quiz" }));
    render(<Home />);
    await waitFor(() => expect(screen.getByRole("heading", { name: "Build a practice set" })).toBeInTheDocument());
    expect(screen.getByRole("slider", { name: /Question count/ })).toHaveValue("10");
    expect(screen.getByRole("button", { name: /Start practice/ })).toBeEnabled();
  });
});
