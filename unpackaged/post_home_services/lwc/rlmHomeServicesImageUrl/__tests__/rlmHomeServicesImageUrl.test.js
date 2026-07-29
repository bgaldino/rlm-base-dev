import { resolveProductImageUrl } from "c/rlmHomeServicesImageUrl";

describe("resolveProductImageUrl", () => {
  it("uses the Experience Cloud static-resource path for guest pages", () => {
    expect(
      resolveProductImageUrl("/resource/HS_DEEP_MON", "vforcesite/s")
    ).toBe("/vforcesite/sfsites/c/resource/HS_DEEP_MON");
  });

  it("supports Experience sites without a URL prefix", () => {
    expect(resolveProductImageUrl("/resource/HS_DEEP_MON", "s")).toBe(
      "/sfsites/c/resource/HS_DEEP_MON"
    );
  });

  it("keeps the standard static-resource path for Lightning pages", () => {
    expect(resolveProductImageUrl("/resource/HS_DEEP_MON")).toBe(
      "/resource/HS_DEEP_MON"
    );
  });

  it("passes external URLs through unchanged", () => {
    const url = "https://example.com/product.png";
    expect(resolveProductImageUrl(url, "vforcesite/s")).toBe(url);
  });

  it("does not double-prefix an Experience static-resource URL", () => {
    const url = "/vforcesite/sfsites/c/resource/HS_DEEP_MON";
    expect(resolveProductImageUrl(url, "vforcesite/s")).toBe(url);
  });

  it("normalizes a static-resource path without a leading slash", () => {
    expect(resolveProductImageUrl("resource/HS_DEEP_MON")).toBe(
      "/resource/HS_DEEP_MON"
    );
  });

  it("returns null for missing URLs", () => {
    expect(resolveProductImageUrl()).toBeNull();
    expect(resolveProductImageUrl("   ")).toBeNull();
  });
});
