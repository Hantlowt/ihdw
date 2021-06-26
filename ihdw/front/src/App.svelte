<script>
	import Loading from  './Loading.svelte';
	import Login from './Login.svelte';
	import Dashboard from './Dashboard.svelte';
	let api;
	let isLoggedPromise;
	const initAPI = () => {
		api = window.api;
		init()
	}
	async function init() {
		isLoggedPromise = api.token_authenticated()
	}
</script>

<svelte:head><link rel="stylesheet" href="https://unpkg.com/mvp.css">
<script src="http://localhost:8000/api.js" on:load={initAPI}></script>
</svelte:head>


{#await isLoggedPromise}
		<Loading enabled={true} />
{:then}
		<Dashboard api={api} on:disconnect={init}/>
{:catch}
		<Login api={api} on:login={init}/>
{/await}
