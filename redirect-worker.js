export default {
    async fetch(request) {
        const url = new URL(request.url);
        const { pathname, search } = url;
        const destinationURL = `https://freepromptbase.com${pathname}${search}`;
        return Response.redirect(destinationURL, 301);
    },
};
