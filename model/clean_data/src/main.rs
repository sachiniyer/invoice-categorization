use clap::{Arg, Command};
use office::{DataType, Excel, Range};
use rust_xlsxwriter::*;
use std::collections::HashMap;
use std::fmt::{Display, Formatter};
use std::fs;
use std::io::{self, Write};

#[derive(Debug, Clone)]
struct DataTypeWrap {
    data_type: DataType,
}

impl Display for DataTypeWrap {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self.data_type {
            DataType::Empty => write!(f, ""),
            DataType::String(ref s) => write!(f, "{}", s),
            DataType::Float(ref n) => write!(f, "{}", n),
            DataType::Int(ref n) => write!(f, "{}", n),
            DataType::Error(ref _e) => write!(f, "{}", "Error"),
            DataType::Bool(ref b) => write!(f, "{}", b),
        }
    }
}

fn print_list<T: Display>(list: Vec<T>) {
    for (i, item) in list.iter().enumerate() {
        println!("{}: {}", i, item);
    }
}

fn print_range(range: &mut Range) -> Result<(), Box<dyn std::error::Error>> {
    let max: usize = format!(
        "{:?}",
        range
            .rows()
            .take(15)
            .flat_map(|i| i.iter())
            .max_by(|x, y| {
                let x_size = format!("{:?}", x).len();
                let y_size = format!("{:?}", y).len();
                x_size.cmp(&y_size)
            })
            .unwrap()
    )
    .len();
    for (i, row) in range.rows().take(10).enumerate() {
        print!("{}: | ", i);
        for cell in row.into_iter().take(10) {
            print!(
                "{:width$} | ",
                DataTypeWrap {
                    data_type: cell.clone()
                },
                width = max
            );
        }
        println!();
    }
    Ok(())
}

fn get_user_input() -> Result<String, Box<dyn std::error::Error>> {
    io::stdout().flush().expect("Failed to flush");
    let mut input_text = String::new();
    io::stdin()
        .read_line(&mut input_text)
        .expect("Failed to read input");
    io::stdout().flush().expect("Failed to flush");
    Ok(input_text.trim().to_string())
}

fn get_user_num() -> Result<usize, Box<dyn std::error::Error>> {
    let input_text = get_user_input()?;
    let number = input_text.trim().parse();
    match number {
        Ok(number) => Ok(number),
        Err(e) => Err(Box::new(e)),
    }
}

fn get_sheet(workbook: &mut Excel) -> Result<String, Box<dyn std::error::Error>> {
    print_list(workbook.sheet_names().unwrap());
    print!("Choose Sheet: ");
    let index = loop {
        match get_user_num() {
            Ok(index) => {
                if index >= workbook.sheet_names().unwrap().len() {
                    println!("Invalid input");
                    continue;
                }
                break index;
            }
            Err(e) => {
                println!("Invalid input {}", e);
                print!("Choose Sheet: ");
                continue;
            }
        }
    };
    Ok(workbook.sheet_names().unwrap()[index].clone())
}

fn get_row_offset(range: &mut Range, message: String) -> Result<usize, Box<dyn std::error::Error>> {
    print_range(range)?;
    print!("{}", message);
    let row = loop {
        match get_user_num() {
            Ok(index) => {
                if index >= range.rows().count() {
                    println!("Invalid input");
                    continue;
                }
                break index;
            }
            Err(e) => {
                println!("Invalid Input: {}", e);
                print!("{}", message);
                continue;
            }
        }
    };
    Ok(row)
}

fn get_column_offset(
    row: Vec<Vec<DataTypeWrap>>,
    message: String,
) -> Result<usize, Box<dyn std::error::Error>> {
    let row: Vec<Vec<DataTypeWrap>> = (0..row[0].len())
        .map(|col| row.iter().map(|row| row[col].clone()).collect())
        .collect();
    let row = row
        .into_iter()
        .map(|x| {
            x.into_iter()
                .map(|x| format!("{}", x))
                .collect::<Vec<String>>()
                .join(" ---- ")
        })
        .collect::<Vec<String>>();
    print_list(row.clone());
    print!("{}", message);
    let column = loop {
        match get_user_num() {
            Ok(index) => {
                if index >= row.len() {
                    println!("Invalid input");
                    continue;
                }
                break index;
            }
            Err(e) => {
                println!("{}", e);
                print!("{}", message);
                continue;
            }
        }
    };
    Ok(column)
}

fn get_offset(
    range: &mut Range,
) -> Result<(usize, HashMap<String, usize>), Box<dyn std::error::Error>> {
    let row = get_row_offset(range, "Choose Row: ".to_string())?;
    let row_iter = range.rows();
    let row_iter = row_iter.skip(row);
    let row_list: Vec<Vec<DataTypeWrap>> = row_iter
        .take(3)
        .map(|x| {
            x.iter()
                .map(|x| DataTypeWrap {
                    data_type: x.clone(),
                })
                .collect()
        })
        .collect();
    let marked_columns = vec!["vendor", "description", "mapping", "label", "split"];
    let mut res = HashMap::new();
    for m in marked_columns.iter() {
        let column = get_column_offset(row_list.clone(), format!("Choice Column {}: ", m))?;
        res.insert(m.to_string(), column);
    }
    Ok((row, res))
}

fn get_column(
    range: &mut Range,
    row_offset: usize,
    column: usize,
) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let mut res = vec![];
    for i in row_offset..range.get_size().0 {
        res.push(
            DataTypeWrap {
                data_type: range.get_value(i, column).clone(),
            }
            .to_string(),
        );
    }
    Ok(res)
}

fn write_column(
    worksheet: &mut Worksheet,
    data: Vec<String>,
    column: usize,
) -> Result<&mut Worksheet, Box<dyn std::error::Error>> {
    Ok(worksheet.write_column(0, column as u16, data)?)
}

fn write_file(
    range: &mut Range,
    row_offset: usize,
    split: usize,
    columns: HashMap<String, usize>,
) -> Result<Workbook, Box<dyn std::error::Error>> {
    let mut workbook = Workbook::new();
    let worksheet = workbook.add_worksheet().set_name("Data")?;
    let mut iter = 0;
    for (_, v) in columns.into_iter() {
        let data = get_column(range, row_offset, v).unwrap();
        let _ = write_column(worksheet, data, iter);
        iter += 1;
    }
    for i in split..range.get_size().1 {
        let data = get_column(range, row_offset, i).unwrap();
        let _ = write_column(worksheet, data, iter);
        iter += 1;
    }
    Ok(workbook)
}

fn confirm_save() -> Result<bool, Box<dyn std::error::Error>> {
    print!("Save? (y/n): ");
    let res = loop {
        match get_user_input() {
            Ok(s) => {
                if s == "y" {
                    break true;
                } else if s == "n" {
                    break false;
                } else {
                    println!("Invalid input");
                    print!("Save? (y/n): ");
                    continue;
                }
            }
            Err(e) => {
                println!("Invalid input: {}", e);
                print!("Save? (y/n): ");
                continue;
            }
        }
    };
    Ok(res)
}

fn process_file(file_path: &std::path::Path, output_dir: &str) -> io::Result<()> {
    let file_name = file_path
        .file_name()
        .unwrap()
        .to_str()
        .expect("Invalid filename");
    println!("File: {}", file_name);
    let mut workbook = Excel::open(file_path).unwrap();
    let sheet = get_sheet(&mut workbook).unwrap();
    println!("Sheet: {}", sheet);

    let (row_offset, mut column_offsets) =
        get_offset(&mut workbook.worksheet_range(&sheet).unwrap()).unwrap();
    println!("Row offset: {}", row_offset);
    println!("Column offset: {:?}", column_offsets);

    let split = column_offsets.remove("split").unwrap();
    let mut new_workbook = write_file(
        &mut workbook.worksheet_range(&sheet).unwrap(),
        row_offset,
        split,
        column_offsets,
    )
    .unwrap();
    let output_file = format!("{}/{}", output_dir, file_name);
    if confirm_save().unwrap() {
        new_workbook.save(output_file).unwrap();
        return Ok(());
    }
    Err(io::Error::new(io::ErrorKind::Other, "User cancelled"))
}

fn process_files(input_dir: &str, output_dir: &str) -> io::Result<()> {
    let files = fs::read_dir(input_dir)?;

    for file in files {
        let file_path = file?.path();
        if file_path.is_file() {
            loop {
                match process_file(&file_path, output_dir) {
                    Ok(_) => break,
                    Err(e) => {
                        println!("Error: {}", e);
                        continue;
                    }
                }
            }
        }
    }

    Ok(())
}

fn main() {
    let matches = Command::new("Data cleaner")
        .version("1.0")
        .author("Sachin Iyer")
        .about("A CLI application to clean excel spreadsheets")
        .arg(
            Arg::new("input")
                .short('i')
                .long("input")
                .value_name("INPUT"),
        )
        .arg(
            Arg::new("output")
                .short('o')
                .long("output")
                .value_name("OUTPUT"),
        )
        .get_matches();

    let input = matches.get_one::<String>("input").unwrap();
    let output = matches.get_one::<String>("output").unwrap();

    match process_files(input, output) {
        Ok(_) => println!("All files processed successfully!"),
        Err(err) => eprintln!("Error: {}", err),
    }
}
