use dotenv::dotenv;
use gloo::file::callbacks::{read_as_bytes, FileReader};
use gloo::file::File;
use gloo::timers::callback::Timeout;
use gloo_net::http::Request;
use serde_json;
use serde_json::json;
use serde_json::Value;
use std::collections::HashMap;
use std::env;
use wasm_bindgen::JsValue;
use web_sys::{DragEvent, Event, FileList, HtmlInputElement};
use yew::TargetCast;
use yew::{html, Callback, Component, Context, Html};

struct FileDetails {
    url: String,
    status: bool,
}

pub enum Msg {
    Loaded(String, String, Vec<u8>),
    Files(Vec<File>),
    FetchBegin,
    FetchEnd,
}

pub struct App {
    readers: HashMap<String, FileReader>,
    files: HashMap<String, FileDetails>,
    timeout: Option<Timeout>,
}

impl Component for App {
    type Message = Msg;
    type Properties = ();

    fn create(ctx: &Context<Self>) -> Self {
        ctx.link().send_message(Msg::FetchBegin);
        Self {
            readers: HashMap::default(),
            files: HashMap::default(),
            timeout: None,
        }
    }

    fn update(&mut self, ctx: &Context<Self>, msg: Self::Message) -> bool {
        match msg {
            Msg::Files(files) => {
                for file in files.into_iter() {
                    let file_name = file.name();
                    let file_type = file.raw_mime_type();

                    let task = {
                        let link = ctx.link().clone();
                        let file_name = file_name.clone();

                        read_as_bytes(&file, move |res| {
                            link.send_message(Msg::Loaded(
                                file_name,
                                file_type,
                                res.expect("failed to read file"),
                            ))
                        })
                    };
                    self.readers.insert(file_name, task);
                }
                true
            }
            Msg::Loaded(file_name, file_type, data) => {
                let url = env::var("API").unwrap() + "/";
                wasm_bindgen_futures::spawn_local(async move {
                    let body = json!({
                        "file_name": file_name.into_bytes(),
                        "file_type": file_type.into_bytes(),
                        "file_data": String::from_utf8_lossy(&data).to_string(),
                    });

                    let js_value = JsValue::from_str(body.to_string().as_str());
                    let _response = Request::post(url.as_str())
                        .body(js_value)
                        .unwrap()
                        .send()
                        .await
                        .unwrap()
                        .status();
                });
                true
            }
            Msg::FetchBegin => {
                let url = env::var("API").unwrap() + "/";
                let ctx = ctx.clone();
                wasm_bindgen_futures::spawn_local(async move {
                    let response: Value = Request::get(url.as_str())
                        .send()
                        .await
                        .unwrap()
                        .json()
                        .await
                        .unwrap();
                    self.files = response
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|k| {
                            let item = k.as_object().unwrap();
                            (
                                item["file_name"].as_str().unwrap().to_string(),
                                FileDetails {
                                    url: item["file_url"].as_str().unwrap().to_string(),
                                    status: item["status"].as_bool().unwrap(),
                                },
                            )
                        })
                        .collect();
                    ctx.link().send_message(Msg::FetchEnd);
                });
                true
            }
            Msg::FetchEnd => {
                let ctx = ctx.clone();
                let handle = Timeout::new(15000, || {
                    ctx.link().send_message(Msg::FetchBegin);
                });
                self.timeout = Some(handle);
                true
            }
        }
    }

    fn view(&self, ctx: &Context<Self>) -> Html {
        html! {
            <div id="wrapper">
                <p id="title">{ "Invoice Categorization" }</p>
                <label for="file-upload">
                    <div
                        id="drop-container"
                        ondrop={ctx.link().callback(|event: DragEvent| {
                            event.prevent_default();
                            let files = event.data_transfer().unwrap().files();
                            Self::upload_files(files)
                        })}
                        ondragover={Callback::from(|event: DragEvent| {
                            event.prevent_default();
                        })}
                        ondragenter={Callback::from(|event: DragEvent| {
                            event.prevent_default();
                        })}
                    >
                        <i class="fa fa-cloud-upload"></i>
                        <p>{"Drop your files here or click to select"}</p>
                    </div>
                </label>
                <input
                    id="file-upload"
                    type="file"
                    accept=".xlsx,.csv"
                    multiple={true}
                    onchange={ctx.link().callback(move |e: Event| {
                        let input: HtmlInputElement = e.target_unchecked_into();
                        Self::upload_files(input.files())
                    })}
                />
                <div id="preview-area">
                    { for self.files.iter().map(|(k, v)| Self::view_file(k.clone(), v)) }
                </div>
            </div>
        }
    }
}

impl App {
    fn view_file(name: String, file: &FileDetails) -> Html {
        html! {
                <a class="preview-title" href={ file.url.clone() } download={ name.clone() }>
                    <button class="preview-button">{ format!("{}", name) }</button>
                    <p> { file.status } </p>
                </a>
        }
    }

    fn upload_files(files: Option<FileList>) -> Msg {
        let mut result = Vec::new();

        if let Some(files) = files {
            let files = js_sys::try_iter(&files)
                .unwrap()
                .unwrap()
                .map(|v| web_sys::File::from(v.unwrap()))
                .map(File::from);
            result.extend(files);
        }
        Msg::Files(result)
    }
}

fn main() {
    dotenv().ok();
    env::var("API").expect("API not set");
    yew::Renderer::<App>::new().render();
}
