/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Bind resources to your worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

export default {
	async fetch(request, env, ctx): Promise<Response> {
		const url = new URL(request.url)
		const filename = url.searchParams.get("file")
		if (!filename) {
			return new Response("No url", {status: 404})
		}
		console.log(typeof env.MY_BUCKET)
		const response = await env.MY_BUCKET.get(filename)
		if (!response) {
			return new Response("File not found", {status: 404})
		}
		return new Response(response.body, {
			headers: {
				"Content-Type": "application/pdf",
				"Content-Disposition": 'attachment; filename="resume.pdf"',
				"Cache-Control": "no-cache"
			}
		})
	},
} satisfies ExportedHandler<Env>;
