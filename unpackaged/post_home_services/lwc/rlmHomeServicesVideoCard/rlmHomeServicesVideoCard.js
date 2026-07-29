import { LightningElement, api } from "lwc";

export default class RlmHomeServicesVideoCard extends LightningElement {
  @api cardTitle = "Home Services Demo Recording";
  @api videoUrl;

  get embedUrl() {
    const url = (this.videoUrl || "").trim();
    if (!url) {
      return undefined;
    }

    const id = this.extractYouTubeId(url);
    return id ? `https://www.youtube.com/embed/${id}` : undefined;
  }

  get hasVideo() {
    return Boolean(this.embedUrl);
  }

  extractYouTubeId(url) {
    const patterns = [
      /youtu\.be\/([\w-]{11})/,
      /youtube\.com\/watch\?v=([\w-]{11})/,
      /youtube\.com\/embed\/([\w-]{11})/,
      /youtube-nocookie\.com\/embed\/([\w-]{11})/
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }

    return null;
  }
}
