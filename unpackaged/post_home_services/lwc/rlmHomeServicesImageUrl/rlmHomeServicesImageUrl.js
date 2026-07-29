const STATIC_RESOURCE_PATH = "/resource/";

function experienceSitePrefix(basePath) {
  const segments = String(basePath || "")
    .split("/")
    .filter(Boolean);
  const pageRouteIndex = segments.indexOf("s");
  const siteSegments =
    pageRouteIndex === -1 ? segments : segments.slice(0, pageRouteIndex);
  return siteSegments.length ? `/${siteSegments.join("/")}` : "";
}

/**
 * Resolves Product2.DisplayUrl for the page that renders it.
 *
 * Static-resource paths use /resource/... in authenticated Lightning pages,
 * while guest-facing Experience pages require
 * <site-prefix>/sfsites/c/resource/....
 * Absolute and other relative URLs pass through unchanged; their hosts must
 * still be allowed by the page's CSP Trusted Sites configuration.
 */
export function resolveProductImageUrl(displayUrl, experienceBasePath = null) {
  if (typeof displayUrl !== "string") {
    return null;
  }

  let url = displayUrl.trim();
  if (!url) {
    return null;
  }

  if (url.startsWith("resource/")) {
    url = `/${url}`;
  }

  if (
    experienceBasePath !== null &&
    experienceBasePath !== undefined &&
    url.startsWith(STATIC_RESOURCE_PATH)
  ) {
    return `${experienceSitePrefix(experienceBasePath)}/sfsites/c${url}`;
  }

  return url;
}
