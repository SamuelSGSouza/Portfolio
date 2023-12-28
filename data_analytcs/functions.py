import pandas as pd
import os
import shutil
from django.conf import settings
from pandas.errors import EmptyDataError, ParserError
import traceback
from sklearn.preprocessing import MinMaxScaler
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import threading
import jellyfish
import base64


class Cleaning():
    def __init__(self, file, filename, handle_null_values="Ignore", handle_outliers="Ignore", 
                handle_duplicates="Ignore", handle_reescale="No"):
        self.file = file
        self.filename = filename
        self.saved_file_path = ""
        self.df = pd.DataFrame()
        self.primary_field = ""
        self.verbose_model = ""
        self.success = []
        self.failures = []
        self.null_values = handle_null_values
        self.outliers = handle_outliers
        self.duplicates = handle_duplicates
        self.reescale = handle_reescale

    def main(self) -> None:
        '''
        This function is the main function of the class. It calls the other functions
        and returns a dict with the results
        '''
        file = self.save_file()
        if not file:
            self.failures.append(f"Error while saving file.")
            return None
        
        self.saved_file_path = file

        #reading the file
        success = self.read_file()
        if not success:
            self.failures.append(f"Error while reading file.")
            return None


        #limpando as colunas
        self.clean_columns()
        #setando os tipos
        self.set_types()

        #handling null values
        self.handle_null_values()

        #handling outliers
        self.handle_outliers()

        #handling duplicates
        self.handle_duplicates()

        #handling reescale
        self.handle_reescale()

        #re-saving the file
        self.saved_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', self.filename)
        self.df.to_csv(self.saved_file_path, index=False, sep=";")

        return None
        
    def save_file(self):
        try:
            #If the directory temp doesn't exist, create it
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp')):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp'))

            #Saving the files in the directory temp
            with open(os.path.join(settings.MEDIA_ROOT, 'temp', self.filename), 'wb+') as destination:
                for chunk in self.file.chunks():
                    destination.write(chunk)

            file = os.path.join(settings.MEDIA_ROOT, 'temp', self.filename)
            self.success.append(f"File saved successfully")
            return file
        except Exception as e:
            self.failures.append(f"Error while saving file.")
            return None

    def read_file(self) -> pd.DataFrame:
        
        try:
            #getting the extension of the file
            ext = self.saved_file_path.split('.')[-1].lower()        
            if ext == 'csv':
                self.df = self.gera_df_csv(self.saved_file_path)
            # elif ext == 'txt':
            #     self.df = self.gera_df_txt(self.saved_file_path)
            # elif ext == 'xlsx' or ext == 'xls':
            #     self.df = self.gera_df_xlsx(self.saved_file_path)
            else:
                self.failures.append(f"File has an invalid extension.")
                return False
            self.success.append(f"File read successfully")
            return True
        except Exception as e:
            self.failures.append(f"Unknown error while reading file.")
            return False
            
    def clean_columns(self) -> dict:
        try:
            df = self.df
            #substituindo /r e /n por ""
            df.columns = df.columns.str.replace('\r', '')
            df.columns = df.columns.str.replace('\n', '')
            df = df.replace('\n', '').replace('\r', '')
            df.columns = df.columns.str.strip()

            #substituindo espaços por _
            df.columns = df.columns.str.replace(' ', '_')
            df.columns = df.columns.str.replace('(', '')
            df.columns = df.columns.str.replace(')', '')
            df.columns = df.columns.str.replace('/', '_')

            self.df = df
            self.success.append(f"Columns cleaned successfully")
        except Exception as e:
            self.failures.append(f"Error while cleaning columns.")

    def set_types(self):
        try:
            #Set the types of the columns
            df = self.df
            all_columns = df.columns.to_list()
            rest_columns = df.columns.to_list()

            #if one of the columns is a number, set the type to float
            for col in all_columns:
                #getting the 5 first values of the column
                first_values = df[col].head().to_list()
                #verifying if the values are numbers
                try:
                    [float(i) for i in first_values]

                    #verifying if the column is float or int by checking the first value
                    if "." in str(first_values[0]):
                        #verifying if the values end with .0
                        verify = [str(value).endswith(".0") for value in first_values]
                        if all(verify):
                            df[col] = df[col].astype('Int64')
                            self.success.append(f"Column >{col}< set to int")
                            rest_columns.remove(col)
                        else:
                            df[col] = df[col].astype('float64')
                            self.success.append(f"Column >{col}< set to float")
                            rest_columns.remove(col)
                             
                    else:
                        #setting the type to int
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                        self.success.append(f"Column >{col}< set to int")
                        rest_columns.remove(col)

                except:
                    pass
                    

            all_columns = rest_columns
            #if one of the columns has less than 10 unique values, set the type to category
            for col in all_columns:
                unique_values = df[col].nunique()
                #if unique values are less than 20% of the total values, set the type to category
                if unique_values < 30:
                    df[col] = df[col].astype('category')
                    self.success.append(f"Column >{col}< set to category")
                    rest_columns.remove(col)
            
            
            

            all_columns = rest_columns
            #if one of the columns has the word date in it, set the type to datetime
            for col in all_columns:
                date_comum_names = [
                    "data", "dt", "date", "dt_", "data_", "dt_nasc", "dt_nascimento", "dt_nasc_",
                    "periodo", "period", "period_", "periodo_", "start_date", "end_date", "start", "end",
                ]
                for name in date_comum_names:
                    if jellyfish.jaro_winkler_similarity(col.lower(), name) > 0.85:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        self.success.append(f"Column >{col}< set to datetime")
                        rest_columns.remove(col)
                        break

            self.df = df
            self.success.append(f"Types set successfully")


        except Exception as e:
            self.failures.append(f"Error while setting types.")
    
    def handle_null_values(self):
        try:
            #handle options: drop, fill, leave
            handle_selected = self.null_values
            if handle_selected == "drop":
                self.df = self.df.dropna()
                self.success.append(f"Null values dropped successfully")

            elif handle_selected == "fill":
                #if the column is a number, fill with the mean
                for col in self.df.columns:
                    try:
                        #verificando se a coluna é numérica
                        if self.df[col].dtype == 'float64' or self.df[col].dtype == 'int64' or self.df[col].dtype == 'int32':
                            self.df[col] = self.df[col].fillna(self.df[col].mean())
                        else:
                            self.df[col] = self.df[col].fillna("")
                    except:
                        self.failures.append(f"Error while handling null values in column {col}.")
                        continue
                self.success.append(f"Null values filled successfully")
        except Exception as e:
            self.failures.append(f"Error while handling null values.")

    def handle_outliers(self):
        #handle options: drop, fill, leave
        handle_selected = self.outliers
        if handle_selected == "Ignore":
            return None
        try:
            #iterando sobre as colunas numéricas
            for col in self.df.columns:
                num_types = ['float64', 'int64', 'int32', 'float32']
                if self.df[col].dtype in num_types:
                    q1 = self.df[col].quantile(0.25)
                    q3 = self.df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - (1.5 * iqr)
                    upper_bound = q3 + (1.5 * iqr)
                    self.df = self.df[(self.df[col] > lower_bound) & (self.df[col] < upper_bound)]
            self.success.append(f"Outliers dropped successfully")
        except Exception as e:
            self.failures.append(f"Error while handling outliers.")
        
    def handle_duplicates(self):
        #handle options: drop, fill, leave
        handle_selected = self.duplicates
        if handle_selected == "Ignore":
            return None
        try:
            self.df = self.df.drop_duplicates()
            self.success.append(f"Duplicates dropped successfully")
        except Exception as e:
            self.failures.append(f"Error while handling duplicates.")

    def handle_reescale(self):
        #handle options: drop, fill, leave
        handle_selected = self.reescale
        if handle_selected == "No":
            return None
        try:
            #rescaling the data
            scaler = MinMaxScaler()
            for col in self.df.columns:
                num_types = ['float64', 'int64', 'int32', 'float32']
                if self.df[col].dtype in num_types:
                    self.df[col] = scaler.fit_transform(self.df[[col]])
            self.success.append(f"Data rescaled successfully")
        except Exception as e:
            self.failures.append(f"Error while rescaling data.")
            
    def detect_separator(self):
        try:
            try:
                with open(self.saved_file_path, 'r', encoding='utf-8') as f:
                    line = f.readline().strip()
            except UnicodeDecodeError:
                with open(self.saved_file_path, 'r', encoding='latin-1') as f:
                    line = f.readline().strip()

            # Conta a ocorrência de cada delimitador na linha
            counts = {
                ',': line.count(','),
                ';': line.count(';'),
                '\t': line.count('\t'),
                '|': line.count('|'),
                '||': line.count('||'),
                ':': line.count(':')
            }

            # Retorna o delimitador que tem a maior contagem
            return True, max(counts, key=counts.get)
            
        except Exception as e:
            return False, ","

    def gera_df_csv(self, arqu) -> pd.DataFrame:
        '''
        Reads the file and generates a dataframe for each file passed to the instance and concatenates them all
        '''
        try:
            # verifying the separator
            success, separador = self.detect_separator()
            if not success:
                self.failures.append(f"Error while detecting separator.")
                return self.df
            try:
                df = pd.read_csv(arqu, encoding="utf-8", sep=separador, low_memory=False,
                                            on_bad_lines='skip', lineterminator='\n')  # lendo o arquivo passado
                encr = "utf-8"
            except:
                df = pd.read_csv(arqu, encoding="latin-1", sep=separador, low_memory=False,
                                            on_bad_lines='skip', lineterminator='\n')
                encr = "latin-1"
            self.success.append(f"Encoding {encr} detected.")

            # excluding line where all fields are empty
            df = df.dropna(how='all')

            
            # verify if the file has empty lines before the data
            columns = df.columns.to_list()
            if type(columns[0]) == float:
                self.failures.append(f"File has empty lines before the data.")
                return self.df
        except EmptyDataError:
            self.failures.append(f"File has an invalid delimiter.")
            return self.df

        except Exception as e:
            self.failures.append(f"Error while reading file.")
            return self.df
        
        #se o df não for um dataframe vazio, junta os dois
        if not self.df.empty:
            self.df = pd.concat([self.df, df])
        else:
            self.df = df
        return self.df

    def gera_df_xlsx(self, arqu) -> pd.DataFrame:
        '''
        gera um dataframe para cada arquivo passado para a instância  e concatena todos eles
        '''
        response = {'ok': True}
        df = pd.DataFrame()
        try:
            # lendo o arquivo passado
            df = pd.read_excel(arqu,engine='openpyxl', keep_default_na=False)
            df = df.dropna(how='all')

            # resolvendo problema de linhas vazias antes dos dados
            colunas = df.columns.to_list()

            # verificando se o arquivo possui linhas vazias antes do texto
            if ("Unnamed" in str(colunas[0])) or type(colunas[0]) == float:
                response = {
                    'ok': False, 'msg': "O arquivo possui linhas vazias ou de comentários antes do conteúdo. Caso não seja possível removê-las converta-o para outro formato e tente novamente"}
                return response

        except EmptyDataError:
            "erro de No columns to parse from file"
            response = {
                'ok': False, 'msg': "O arquivo possui possui uma delimitação incompreensivel entre as colunas. Converta-o para outro formato e tente novamente"}
            return response
        
        except Exception as e:
            return {'ok': False, 'msg': f'Erro do tipo {type(e)} no arquivo {arqu} durante a geração dos dados. Erro: {e}'}

        df = pd.concat([df, df])
        # df = df[:800000] #TODO!: tirar essa linha
        self.df = pd.concat([self.df, df])
        return response

    def gera_df_txt(self, arqu) -> pd.DataFrame:
        '''
        gera um dataframe para cada arquivo passado para a instância  e concatena todos eles
        '''
        response = {'ok': True}
        df = pd.DataFrame()
        i = 0
        i += 1
        try:
            #verificando se o sep é ; ou ,
            separador = self.detect_separator(arqu)
            try:
                df = pd.read_table(arqu, encoding="utf-8", sep=separador, low_memory=False)
            except:
                df = pd.read_table(arqu, encoding="latin-1", sep=separador, low_memory=False)    
            # excluindo linha onde todos os campos forem vazios
            df = df.dropna(how='all')

            # resolvendo problema de linhas vazias antes dos dados
            colunas = df.columns.to_list()
            # verificando se o arquivo possui linhas vazias antes do texto
            if ("Unnamed" in str(colunas[0])) or type(colunas[0]) == float:
                response = {
                    'ok': False, 'msg': "O arquivo possui linhas vazias ou de comentários antes do conteúdo. Caso não seja possível removê-las converta-o para outro formato e tente novamente"}
                return response
            

        except EmptyDataError:
            "erro de No columns to parse from file"
            response = {
                'ok': False, 'msg': "O arquivo possui possui uma delimitação incompreensivel entre as colunas. Converta-o para outro formato e tente novamente"}
            return response

        except Exception as e:
            return {'ok': False, 'msg': f'Erro do tipo {type(e)} no arquivo {arqu} durante a geração dos dados. Erro: {e}'}

        try:
            df = pd.concat([df, df])
        except Exception as e:
            return {'ok': False, 'msg': f'Erro do tipo {type(e)} no arquivo {arqu} durante a concatenação dos dados. Erro: {e}'}
        
        
        
        self.df = pd.concat([self.df, df])
        #se o df tiver menos que 2 colunas levanta ParserError
        if len(self.df.columns) < 2:
            raise ParserError
        return response
    
class Analytics():
    def __init__(self, df):
        self.df = df
        self.success = []
        self.failures = []
        self.hist_images = []
        self.boxplot_images = []
        self.cor_matrix_image = ""

    def main(self):
        if self.df.empty:
            self.failures.append(f"Dataframe is empty.")
            return False
        
        #verifying if there are numeric columns
        num_types = ['float64', 'int64', 'int32', 'float32']
        numeric_columns = self.df.select_dtypes(include=num_types).columns.to_list()
        if len(numeric_columns) == 0:
            self.failures.append(f"No numeric columns found.")
            return False
        else:
            self.generate_cor_matrix()
            self.generate_boxplot_graphic()
    
        self.generate_hist_graphic()
   
    def generate_cor_matrix(self):
        try:
            #getting just the numeric columns
            num_types = ['float64', 'int64', 'int32', 'float32']
            df = self.df.select_dtypes(include=num_types)
            #getting the correlation matrix
            corr = df.corr()
            #plotting the correlation matrix
            plt.matshow(corr)
            plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
            plt.yticks(range(len(corr.columns)), corr.columns)
            plt.colorbar()

            self.success.append(f"Correlation matrix generated successfully")

            #saving the plot
            path = os.path.join(settings.MEDIA_ROOT, 'temp', f"correlation_matrix.png")
            plt.savefig(path)

            #closing the plot
            plt.close()

            #converting the image to base64
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                encoded_string = encoded_string.decode('utf-8')
            #getting the image path
            self.cor_matrix_image = encoded_string

            #removing the image
            os.remove(path)
            return True
        except Exception as e:
            self.failures.append(f"Error while generating correlation matrix.")
            return False

    def generate_hist_graphic(self):
        #verifying if there are date columns
        date_columns = self.df.select_dtypes(include=['datetime64']).columns.to_list()
        
        #verifying if there are columns with similarity with "date", "year", "month", "day"
        columns = self.df.columns.to_list()
        date_names = ["date", "year", "month", "day"]
        for col in columns:
            for name in date_names:
                if jellyfish.jaro_winkler_similarity(col.lower(), name) > 0.85:
                    date_columns.append(col)
                    break
        
        if len(date_columns) == 0:
            return False
        
        #getting numeric columns if it's name is not in the list of date columns
        numeric_columns = []
        num_types = ['float64', 'int64', 'int32', 'float32']
        for col in self.df.select_dtypes(include=num_types).columns.to_list():
            if col not in date_columns:
                numeric_columns.append(col)

        #iterating over the columns to draw an line plot for every date column
        for date_col in date_columns:
            for num_col in numeric_columns:
                for cat_col in self.df.select_dtypes(include=["category"]).columns.to_list():
                    try:
                        # Create a figure and an axes.
                        fig, ax = plt.subplots()
                        fig.set_size_inches(15, 5)

                        #removing the null values
                        n_df = self.df.dropna(subset=[cat_col, num_col, date_col])
                        n_df= n_df.sort_values(date_col)

                        # Iterating over the groups
                        for categoria, grupo in n_df.groupby(cat_col):
                            ax.plot(grupo[date_col], grupo[num_col], label=categoria)

                        # Add some axis labels
                        ax.set_xlabel(date_col)
                        ax.set_ylabel(num_col)

                        # Add a legend
                        ax.legend()

                        #add a title
                        ax.set_title(f"Line plot for Column {num_col} and Category {cat_col}")

                        path = os.path.join(settings.MEDIA_ROOT, 'temp', f"hist_{date_col}_{num_col}_{cat_col}.png")

                        #saving the plot
                        plt.savefig(path)  

                        #closing the plot
                        plt.close()

                        #converting the image to base64
                        with open(path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                            encoded_string = encoded_string.decode('utf-8')

                        #getting the image path
                        self.hist_images.append(encoded_string)

                        #removing the image
                        os.remove(path)
                    except Exception as e:
                        continue
        self.success.append(f"Histograms generated successfully")
        return True
        
    def generate_boxplot_graphic(self):
        #iterating over the columns to make the boxplot for every numeric column
        num_types = ['float64', 'int64', 'int32', 'float32']
        category_columns = self.df.select_dtypes(include=["category"]).columns.to_list()
        for col in self.df.select_dtypes(include=num_types).columns.to_list():
            for cat_col in category_columns:
                try:
                    cat_df = self.df[self.df[cat_col].notna()]
                    categories = cat_df[cat_col].unique()
                    for category in categories:
                        #verificando se a coluna é numérica
                        if self.df[col].dtype in num_types:
                            #gerando boxplot deitado
                            figure = plt.figure(figsize=(8, 5))
                            ax = figure.add_subplot(121)
                            ax.boxplot(cat_df[cat_df[cat_col] == category][col],vert=False)
                            ax.set_title(f"Boxplot for Column {col} and Category {category}")
                            ax.set_xlabel(col)
                            ax.set_ylabel("")

                            path = os.path.join(settings.MEDIA_ROOT, 'temp', f"boxplot_{col}_{cat_col}_{category}.png")
                            #saving the plot
                            plt.savefig(path)
                
                            #converting the image to base64
                            with open(path, "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())
                                encoded_string = encoded_string.decode('utf-8')

                            #getting the image path
                            self.boxplot_images.append(encoded_string)

                            #removing the image
                            os.remove(path)

                except Exception as e:
                    self.failures.append(f"Error while generating boxplot for column {col}.")
                    continue
                
        self.success.append(f"Boxplot for column {col} generated successfully")
        return True